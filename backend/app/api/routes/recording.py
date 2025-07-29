from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import os
from datetime import datetime
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.meeting import Meeting, AudioChunk
from app.services.auth_service import AuthService
from app.services.recording_service import RecordingService
from app.services.export_service import ExportService
from app.middleware.rate_limit import create_rate_limit_decorator

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# レスポンスモデル
class RecordingResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class MeetingResponse(BaseModel):
    id: int
    title: str
    status: str
    drive_file_url: Optional[str] = None
    created_at: datetime
    whisper_tokens: Optional[int] = None
    gpt_tokens: Optional[int] = None

class StartRecordingRequest(BaseModel):
    title: str

class UploadChunkRequest(BaseModel):
    meeting_id: int
    chunk_number: int

class EndRecordingRequest(BaseModel):
    meeting_id: int

class ExportRequest(BaseModel):
    meeting_id: int
    format: str  # "pdf" or "docx"

@router.post("/start", response_model=RecordingResponse)
async def start_recording(
    request: StartRecordingRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """録音開始"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        # プレミアム権限チェック
        is_premium = user.is_premium == "true"
        print(f"DEBUG: プレミアム状態チェック - user_id: {user.id}, is_premium: {user.is_premium}, type: {type(user.is_premium)}")
        print(f"DEBUG: プレミアム判定結果: {is_premium}")
        
        # 無料期間チェック
        if not auth_service.is_trial_valid(user):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="無料期間が終了しました。有料プランにアップグレードしてください。"
            )
        
        # 録音時間制限を設定（無料ユーザーは30分、プレミアムユーザーは2時間）
        max_duration = 120 if is_premium else 30  # プレミアム: 2時間、無料: 30分
        print(f"DEBUG: 録音時間制限設定 - max_duration: {max_duration}分 (プレミアム: {is_premium})")
        
        # 議事録作成
        meeting = Meeting(
            user_id=user.id,
            title=request.title,
            status="recording",
            max_duration=max_duration
        )
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
        
        return RecordingResponse(
            success=True,
            message="録音を開始しました",
            data={
                "meeting": MeetingResponse(
                    id=meeting.id,
                    title=meeting.title,
                    status=meeting.status,
                    drive_file_url=meeting.drive_file_url,
                    created_at=meeting.created_at,
                    whisper_tokens=meeting.whisper_tokens,
                    gpt_tokens=meeting.gpt_tokens
                ).dict()
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"録音開始に失敗しました: {str(e)}"
        )

@router.post("/chunk", response_model=RecordingResponse)
async def upload_chunk(
    meeting_id: int = Form(...),
    chunk_number: int = Form(...),
    audio_file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """音声チャンクのアップロード"""
    print("DEBUG: チャンクアップロードエンドポイント開始")
    try:
        print(f"DEBUG: チャンクアップロード開始 - meeting_id: {meeting_id}, chunk_number: {chunk_number}")
        print(f"DEBUG: ファイル名: {audio_file.filename}, サイズ: {audio_file.size if hasattr(audio_file, 'size') else 'unknown'}")
        print(f"DEBUG: content_type: {audio_file.content_type}")
        
        # ファイル形式の検証
        if not audio_file.content_type.startswith('audio/'):
            print(f"DEBUG: ファイル形式エラー - content_type: {audio_file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="音声ファイルのみアップロード可能です"
            )
        
        # ファイルサイズの検証
        content = await audio_file.read()
        print(f"DEBUG: ファイルサイズ: {len(content)} bytes")
        if len(content) > settings.MAX_FILE_SIZE:
            print(f"DEBUG: ファイルサイズ超過 - {len(content)} > {settings.MAX_FILE_SIZE}")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"ファイルサイズが大きすぎます。最大{settings.MAX_FILE_SIZE // (1024*1024)}MBまで"
            )
        
        # ファイルポインタを先頭に戻す
        await audio_file.seek(0)
        
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        print(f"DEBUG: ユーザー認証 - email: {user_email}")
        
        # 議事録の確認
        meeting = db.query(Meeting).filter(
            Meeting.id == meeting_id,
            Meeting.user_id == user.id
        ).first()
        
        if not meeting:
            print(f"DEBUG: 議事録が見つかりません - meeting_id: {meeting_id}, user_id: {user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="議事録が見つかりません"
            )
        
        print(f"DEBUG: 議事録確認 - status: {meeting.status}")
        if meeting.status not in ["recording", "completed", "processing"]:
            print(f"DEBUG: 議事録ステータスエラー - status: {meeting.status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="録音中、処理中、または完了した議事録のみチャンクをアップロードできます"
            )
        
        # 録音時間制限チェック
        if meeting.status == "recording" and meeting.max_duration:
            from datetime import datetime
            # 録音開始時刻を現在時刻に更新（初回チャンクの場合）
            if chunk_number == 0:
                meeting.created_at = datetime.now()
                db.commit()
                print(f"DEBUG: 録音開始時刻を更新 - meeting_id: {meeting_id}")
            
            elapsed_minutes = (datetime.now() - meeting.created_at).total_seconds() / 60
            if elapsed_minutes >= meeting.max_duration:
                # 録音時間制限に達した場合、録音を自動停止
                meeting.status = "completed"
                db.commit()
                print(f"DEBUG: 録音時間制限に達しました - {elapsed_minutes:.1f}分 >= {meeting.max_duration}分")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"録音時間制限（{meeting.max_duration}分）に達しました。プレミアムプランにアップグレードすると無制限録音が可能です。"
                )
        
        # ファイル保存
        recording_service = RecordingService()
        filename = await recording_service.save_chunk(audio_file, meeting_id, chunk_number)
        print(f"DEBUG: ファイル保存完了 - filename: {filename}")
        
        # データベースに記録
        chunk = AudioChunk(
            meeting_id=meeting_id,
            chunk_number=chunk_number,
            filename=filename,
            status="uploaded"
        )
        db.add(chunk)
        db.commit()
        print(f"DEBUG: データベース保存完了 - chunk_id: {chunk.id}")
        
        return RecordingResponse(
            success=True,
            message="チャンクをアップロードしました",
            data={
                "chunk_id": chunk.id,
                "filename": filename,
                "status": "uploaded",
                "meeting_id": meeting_id
            }
        )
    
    except HTTPException:
        print("DEBUG: HTTPException発生")
        raise
    except Exception as e:
        print(f"DEBUG: 予期しないエラー - {str(e)}")
        import traceback
        print(f"DEBUG: 詳細エラー: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"チャンクアップロードに失敗しました: {str(e)}"
        )

@router.post("/end", response_model=RecordingResponse)
async def end_recording(
    request: EndRecordingRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """録音終了と要約処理開始"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        # 議事録の確認
        meeting = db.query(Meeting).filter(
            Meeting.id == request.meeting_id,
            Meeting.user_id == user.id
        ).first()
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="議事録が見つかりません"
            )
        
        if meeting.status != "recording":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="録音中の議事録のみ終了できます"
            )
        
        # ステータスを処理中に変更
        meeting.status = "processing"
        db.commit()
        
        # 要約処理を開始（非同期）
        recording_service = RecordingService()
        try:
            # チャンクがアップロードされるまで少し待つ
            import asyncio
            await asyncio.sleep(5)  # 待機時間を増加
            
            print(f"DEBUG: 要約処理開始 - meeting_id: {request.meeting_id}")
            await recording_service.process_meeting(request.meeting_id, db)
            print(f"DEBUG: 要約処理完了 - meeting_id: {request.meeting_id}")
            
            # 利用回数を増加
            user.usage_count += 1
            db.commit()
            
            # ステータスを完了に変更
            meeting.status = "completed"
            db.commit()
            
        except Exception as e:
            print(f"要約処理エラー: {str(e)}")
            import traceback
            print(f"エラー詳細: {traceback.format_exc()}")
            # エラーが発生してもステータスをcompletedに変更
            meeting.status = "completed"
            db.commit()
        
        return RecordingResponse(
            success=True,
            message="録音を終了し、要約処理を開始しました",
            data={
                "meeting_id": request.meeting_id,
                "status": "processing"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"録音終了に失敗しました: {str(e)}"
        )

@router.get("/status/{meeting_id}", response_model=RecordingResponse)
async def get_recording_status(
    meeting_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """録音・処理状況の取得"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        # 議事録の確認
        meeting = db.query(Meeting).filter(
            Meeting.id == meeting_id,
            Meeting.user_id == user.id
        ).first()
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="議事録が見つかりません"
            )
        
        return RecordingResponse(
            success=True,
            message="録音状況を取得しました",
            data={
                "meeting": MeetingResponse(
                    id=meeting.id,
                    title=meeting.title,
                    status=meeting.status,
                    drive_file_url=meeting.drive_file_url,
                    created_at=meeting.created_at,
                    whisper_tokens=meeting.whisper_tokens,
                    gpt_tokens=meeting.gpt_tokens
                ).dict()
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"状況取得に失敗しました: {str(e)}"
        )

@router.get("/list", response_model=RecordingResponse)
async def get_recording_list(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """ユーザーの録音一覧を取得"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        # ユーザーの議事録一覧を取得
        meetings = db.query(Meeting).filter(
            Meeting.user_id == user.id
        ).order_by(Meeting.created_at.desc()).all()
        
        return RecordingResponse(
            success=True,
            message="録音一覧を取得しました",
            data={
                "meetings": [
                    MeetingResponse(
                        id=meeting.id,
                        title=meeting.title,
                        status=meeting.status,
                        drive_file_url=meeting.drive_file_url,
                        created_at=meeting.created_at,
                        whisper_tokens=meeting.whisper_tokens,
                        gpt_tokens=meeting.gpt_tokens
                    ).dict()
                    for meeting in meetings
                ]
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"録音一覧の取得に失敗しました: {str(e)}"
        )

@router.delete("/{meeting_id}", response_model=RecordingResponse)
async def delete_recording(
    meeting_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """録音の削除"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        # 議事録の確認
        meeting = db.query(Meeting).filter(
            Meeting.id == meeting_id,
            Meeting.user_id == user.id
        ).first()
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="議事録が見つかりません"
            )
        
        # 関連するチャンクも削除
        chunks = db.query(AudioChunk).filter(AudioChunk.meeting_id == meeting_id).all()
        for chunk in chunks:
            db.delete(chunk)
        
        # 議事録を削除
        db.delete(meeting)
        db.commit()
        
        return RecordingResponse(
            success=True,
            message="録音を削除しました",
            data={
                "meeting_id": meeting_id
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"録音の削除に失敗しました: {str(e)}"
        )

@router.get("/health", response_model=RecordingResponse)
async def recording_health_check():
    """録音APIのヘルスチェック"""
    return RecordingResponse(
        success=True,
        message="録音APIは正常に動作しています",
        data={
            "version": "1.0.0",
            "endpoints": [
                "POST /api/recording/start",
                "POST /api/recording/chunk",
                "POST /api/recording/end",
                "GET /api/recording/status/{meeting_id}",
                "GET /api/recording/list",
                "DELETE /api/recording/{meeting_id}"
            ]
        }
    )

@router.get("/summary/{meeting_id}")
async def get_summary(
    meeting_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """要約内容を取得"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        # 議事録の確認
        meeting = db.query(Meeting).filter(
            Meeting.id == meeting_id,
            Meeting.user_id == user.id
        ).first()
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="議事録が見つかりません"
            )
        
        # ファイルパスの生成（summariesディレクトリを参照）
        import os
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        summaries_dir = os.path.join(current_dir, "..", "summaries")
        print(f"DEBUG: current_dir = {current_dir}")
        print(f"DEBUG: summaries_dir = {summaries_dir}")
        print(f"DEBUG: summaries_dir exists = {os.path.exists(summaries_dir)}")
        
        # 議事録IDに基づいてファイルを検索
        import glob
        pattern = os.path.join(summaries_dir, f"*_議事録_{meeting_id}.txt")
        print(f"DEBUG: pattern = {pattern}")
        matching_files = glob.glob(pattern)
        print(f"DEBUG: matching_files = {matching_files}")
        
        # ディレクトリ内の全ファイルを確認
        all_files = glob.glob(os.path.join(summaries_dir, "*.txt"))
        print(f"DEBUG: all_files in summaries = {all_files}")
        
        if not matching_files:
            # ファイルが見つからない場合、利用可能なファイルを表示
            available_ids = []
            for file in all_files:
                filename = os.path.basename(file)
                if "_議事録_" in filename:
                    try:
                        file_id = filename.split("_議事録_")[1].replace(".txt", "")
                        available_ids.append(file_id)
                    except:
                        pass
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"要約ファイルが見つかりません。利用可能なID: {available_ids}"
            )
        
        file_path = matching_files[0]  # 最初に見つかったファイルを使用
        print(f"DEBUG: selected file_path = {file_path}")
        
        # ファイル内容を読み込んで返す
        with open(file_path, 'r', encoding='utf-8') as f:
            summary_content = f.read()
        
        return RecordingResponse(
            success=True,
            message="要約を取得しました",
            data={
                "summary": summary_content,
                "meeting_id": meeting_id
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"要約取得に失敗しました: {str(e)}"
        )

@router.get("/download/{meeting_id}")
async def download_summary(
    meeting_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """要約ファイルのダウンロード"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        # 議事録の確認
        meeting = db.query(Meeting).filter(
            Meeting.id == meeting_id,
            Meeting.user_id == user.id
        ).first()
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="議事録が見つかりません"
            )
        
        # ファイルパスの生成（summariesディレクトリを参照）
        import os
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        summaries_dir = os.path.join(current_dir, "..", "summaries")
        
        # 議事録IDに基づいてファイルを検索
        import glob
        pattern = os.path.join(summaries_dir, f"*_議事録_{meeting_id}.txt")
        matching_files = glob.glob(pattern)
        
        if not matching_files:
            # ファイルが見つからない場合、利用可能なファイルを表示
            all_files = glob.glob(os.path.join(summaries_dir, "*.txt"))
            available_ids = []
            for file in all_files:
                filename = os.path.basename(file)
                if "_議事録_" in filename:
                    try:
                        file_id = filename.split("_議事録_")[1].replace(".txt", "")
                        available_ids.append(file_id)
                    except:
                        pass
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"要約ファイルが見つかりません。利用可能なID: {available_ids}"
            )
        
        file_path = matching_files[0]  # 最初に見つかったファイルを使用
        
        # ファイルを返す
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='text/plain'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ファイルダウンロードに失敗しました: {str(e)}"
        )

@router.get("/storage", response_model=RecordingResponse)
async def get_storage_info(
    token: str = Depends(oauth2_scheme)
):
    """ストレージ使用量の取得"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        
        # ストレージ情報を取得
        recording_service = RecordingService()
        storage_info = recording_service.get_storage_usage()
        
        return RecordingResponse(
            success=True,
            message="ストレージ情報を取得しました",
            data={
                "storage": storage_info
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ストレージ情報の取得に失敗しました: {str(e)}"
        )

@router.post("/export", response_model=RecordingResponse)
async def export_summary(
    request: ExportRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """要約をエクスポート"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        # プレミアム権限チェック
        is_premium = user.is_premium == "true"
        if not is_premium:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="エクスポート機能はプレミアムプランのみ利用可能です"
            )
        
        # 議事録の確認
        meeting = db.query(Meeting).filter(
            Meeting.id == request.meeting_id,
            Meeting.user_id == user.id
        ).first()
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="議事録が見つかりません"
            )
        
        if meeting.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="完了した議事録のみエクスポート可能です"
            )
        
        # 要約ファイルを読み込み
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{timestamp}_議事録_{meeting.id}.txt"
        
        # summariesディレクトリからファイルを検索
        current_dir = os.path.dirname(os.path.abspath(__file__))
        summaries_dir = os.path.join(current_dir, "..", "..", "..", "summaries")
        
        print(f"DEBUG: current_dir = {current_dir}")
        print(f"DEBUG: summaries_dir = {summaries_dir}")
        print(f"DEBUG: summaries_dir exists = {os.path.exists(summaries_dir)}")
        
        # パターンマッチングでファイルを検索
        import glob
        pattern = os.path.join(summaries_dir, f"*_議事録_{meeting.id}.txt")
        print(f"DEBUG: pattern = {pattern}")
        matching_files = glob.glob(pattern)
        print(f"DEBUG: matching_files = {matching_files}")
        
        if not matching_files:
            # ディレクトリ内の全ファイルを確認
            all_files = glob.glob(os.path.join(summaries_dir, "*"))
            print(f"DEBUG: all_files in summaries = {all_files}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="要約ファイルが見つかりません"
            )
        
        file_path = matching_files[0]
        print(f"DEBUG: selected file_path = {file_path}")
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="要約ファイルが見つかりません"
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            summary_content = f.read()
        
        # エクスポートサービスを使用してファイルを生成
        export_service = ExportService()
        
        if request.format.lower() == "pdf":
            export_path = export_service.export_to_pdf(meeting.title, summary_content, meeting.id)
            download_url = f"/api/recording/download-export/{os.path.basename(export_path)}"
        elif request.format.lower() == "docx":
            export_path = export_service.export_to_word(meeting.title, summary_content, meeting.id)
            download_url = f"/api/recording/download-export/{os.path.basename(export_path)}"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="サポートされていない形式です。pdfまたはdocxを指定してください"
            )
        
        return RecordingResponse(
            success=True,
            message=f"{request.format.upper()}ファイルを生成しました",
            data={
                "download_url": download_url,
                "filename": os.path.basename(export_path),
                "format": request.format.lower()
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"エクスポートに失敗しました: {str(e)}"
        )

@router.get("/download-export/{filename}")
async def download_export(
    filename: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """エクスポートファイルをダウンロード"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        # プレミアム権限チェック
        is_premium = user.is_premium == "true"
        if not is_premium:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="エクスポート機能はプレミアムプランのみ利用可能です"
            )
        
        # ファイルパスを構築（exportsディレクトリを確認）
        export_dir = os.path.join(settings.UPLOAD_DIR, "exports")
        file_path = os.path.join(export_dir, filename)
        
        print(f"DEBUG: export_dir = {export_dir}")
        print(f"DEBUG: file_path = {file_path}")
        print(f"DEBUG: file_path exists = {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            # ディレクトリ内の全ファイルを確認
            import glob
            all_files = glob.glob(os.path.join(export_dir, "*"))
            print(f"DEBUG: all_files in exports = {all_files}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ファイルが見つかりません"
            )
        
        # ファイルを返す
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: ダウンロードエラー - {str(e)}")
        import traceback
        print(f"DEBUG: 詳細エラー: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ファイルダウンロードに失敗しました: {str(e)}"
        ) 