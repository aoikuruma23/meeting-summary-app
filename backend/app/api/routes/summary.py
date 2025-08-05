from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.services.summary_service import SummaryService
from app.services.productivity_service import ProductivityService
from app.models.meeting import Meeting, Speaker, Utterance
from typing import Dict, Any
import json
import os

router = APIRouter(tags=["summary"])

@router.get("/{meeting_id}")
async def get_summary(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """要約を取得"""
    try:
        # 会議データを取得
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise HTTPException(status_code=404, detail="会議が見つかりません")
        
        if not meeting.summary:
            raise HTTPException(status_code=404, detail="要約が見つかりません")
        
        return {
            "success": True,
            "message": "要約を取得しました",
            "data": {
                "meeting_id": meeting_id,
                "summary": meeting.summary,
                "title": meeting.title,
                "status": meeting.status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"要約取得に失敗しました: {str(e)}")

@router.post("/export/{meeting_id}")
async def export_summary(
    meeting_id: int,
    format: str = "pdf",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """要約をエクスポート"""
    try:
        # プレミアム権限チェック
        is_premium = current_user.is_premium == "true"
        if not is_premium:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="エクスポート機能はプレミアムプランのみ利用可能です。プレミアムプランにアップグレードしてください。"
            )
        
        # 会議データを取得
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise HTTPException(status_code=404, detail="会議が見つかりません")
        
        if not meeting.summary:
            raise HTTPException(status_code=404, detail="要約が見つかりません")
        
        # エクスポートサービスを使用
        from app.services.export_service import ExportService
        export_service = ExportService()
        
        if format == "pdf":
            file_path = await export_service.export_to_pdf(meeting)
        elif format == "docx":
            file_path = await export_service.export_to_docx(meeting)
        else:
            raise HTTPException(status_code=400, detail="サポートされていない形式です")
        
        return {
            "success": True,
            "message": f"要約を{format.upper()}形式でエクスポートしました",
            "data": {
                "file_path": file_path,
                "filename": os.path.basename(file_path),
                "download_url": f"/api/summary/download/{os.path.basename(file_path)}",
                "format": format
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エクスポートに失敗しました: {str(e)}")

@router.get("/health")
async def health_check():
    """要約APIのヘルスチェック"""
    return {
        "success": True,
        "message": "要約APIは正常に動作しています",
        "data": {
            "version": "1.0.0",
            "endpoints": [
                "POST /api/summary/regenerate/{meeting_id}",
                "GET /api/summary/speaker/{meeting_id}",
                "GET /api/summary/productivity/{meeting_id}"
            ]
        }
    }

@router.post("/regenerate/{meeting_id}")
async def regenerate_summary(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """要約を再生成"""
    try:
        # 会議データを取得
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise HTTPException(status_code=404, detail="会議が見つかりません")
        
        if not meeting.transcript:
            raise HTTPException(status_code=400, detail="転写データがありません")
        
        # 参加者情報を取得
        participants = []
        if meeting.participants:
            try:
                participants = json.loads(meeting.participants)
            except:
                participants = []
        
        # 要約を再生成
        summary_service = SummaryService()
        new_summary = await summary_service.generate_summary(
            meeting.transcript, 
            participants
        )
        
        # データベースを更新
        meeting.summary = new_summary
        db.commit()
        
        return {"message": "要約を再生成しました", "summary": new_summary}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"要約再生成に失敗しました: {str(e)}")

@router.get("/speaker/{meeting_id}")
async def get_speaker_summary(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """話者別要約を取得"""
    try:
        # 会議データを取得
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise HTTPException(status_code=404, detail="会議が見つかりません")
        
        # 話者データを取得
        speakers = db.query(Speaker).filter(Speaker.meeting_id == meeting_id).all()
        if not speakers:
            raise HTTPException(status_code=404, detail="話者データが見つかりません")
        
        # 話者データを構造化
        speakers_data = {"speakers": {}}
        for speaker in speakers:
            utterances = db.query(Utterance).filter(Utterance.speaker_id == speaker.id).all()
            speakers_data["speakers"][speaker.speaker_id] = {
                "id": speaker.speaker_id,
                "name": speaker.name,
                "utterances": [
                    {
                        "start": utt.start_time,
                        "end": utt.end_time,
                        "text": utt.text,
                        "confidence": utt.confidence
                    }
                    for utt in utterances
                ]
            }
        
        # 話者別要約を生成
        summary_service = SummaryService()
        speaker_summary = await summary_service.generate_speaker_summary(speakers_data)
        
        # 生産性分析
        productivity_service = ProductivityService()
        speaker_analysis = productivity_service.analyze_speaker_contribution(
            list(speakers_data["speakers"].values())
        )
        
        return {
            "speaker_summary": speaker_summary,
            "speaker_analysis": speaker_analysis,
            "speakers_data": speakers_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"話者別要約取得に失敗しました: {str(e)}")

@router.get("/productivity/{meeting_id}")
async def get_productivity_report(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """生産性レポートを取得"""
    try:
        # 会議データを取得
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise HTTPException(status_code=404, detail="会議が見つかりません")
        
        # 話者データを取得
        speakers = db.query(Speaker).filter(Speaker.meeting_id == meeting_id).all()
        
        # 会議データを構造化
        meeting_data = {
            "scheduled_duration": meeting.scheduled_duration,
            "actual_duration": meeting.actual_duration,
            "topic_count": meeting.topic_count,
            "completed_topics": meeting.completed_topics,
            "decision_count": meeting.decision_count,
            "action_item_count": meeting.action_item_count,
            "participant_count": meeting.participant_count,
            "speakers": [
                {
                    "id": speaker.speaker_id,
                    "name": speaker.name,
                    "utterances": [
                        {
                            "start": utt.start_time,
                            "end": utt.end_time,
                            "text": utt.text
                        }
                        for utt in db.query(Utterance).filter(Utterance.speaker_id == speaker.id).all()
                    ]
                }
                for speaker in speakers
            ]
        }
        
        # 生産性分析
        productivity_service = ProductivityService()
        efficiency_report = productivity_service.calculate_meeting_efficiency(meeting_data)
        speaker_analysis = productivity_service.analyze_speaker_contribution(meeting_data["speakers"])
        
        return {
            "meeting_id": meeting_id,
            "efficiency_report": efficiency_report,
            "speaker_analysis": speaker_analysis,
            "meeting_data": meeting_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生産性レポート取得に失敗しました: {str(e)}")

@router.get("/download/{filename}")
async def download_export(
    filename: str,
    current_user = Depends(get_current_user)
):
    """エクスポートファイルをダウンロード"""
    try:
        # エクスポートディレクトリのパスを構築
        export_dir = os.path.join("uploads", "exports")
        file_path = os.path.join(export_dir, filename)
        
        # ファイルの存在確認
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")
        
        # ファイルを返す
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルダウンロードに失敗しました: {str(e)}") 