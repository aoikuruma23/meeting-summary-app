import os
import aiofiles
from datetime import datetime
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.meeting import Meeting, AudioChunk
from app.services.whisper_service import WhisperService
from app.services.summary_service import SummaryService

class RecordingService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.whisper_service = WhisperService()
        self.summary_service = SummaryService()
        
        # アップロードディレクトリの作成
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_chunk(self, audio_file: UploadFile, meeting_id: int, chunk_number: int) -> str:
        """音声チャンクを保存"""
        try:
            print(f"DEBUG: save_chunk開始 - meeting_id: {meeting_id}, chunk_number: {chunk_number}")
            print(f"DEBUG: ファイル名: {audio_file.filename}, content_type: {audio_file.content_type}")
            
            # ファイル名の生成（元の拡張子を保持）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_ext = os.path.splitext(audio_file.filename)[1] if audio_file.filename else '.webm'
            filename = f"meeting_{meeting_id}_chunk_{chunk_number}_{timestamp}{original_ext}"
            file_path = os.path.join(self.upload_dir, filename)
            
            print(f"DEBUG: 保存先パス: {file_path}")
            print(f"DEBUG: upload_dir存在確認: {os.path.exists(self.upload_dir)}")
            
            # ファイルの保存
            content = await audio_file.read()
            print(f"DEBUG: ファイルサイズ: {len(content)} bytes")
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            print(f"DEBUG: ファイル保存完了: {filename}")
            return filename
        
        except Exception as e:
            print(f"DEBUG: save_chunkエラー - {str(e)}")
            raise Exception(f"音声ファイルの保存に失敗しました: {str(e)}")
    
    async def process_meeting(self, meeting_id: int, db: Optional[Session] = None):
        """議事録の処理（文字起こし・要約・保存）"""
        try:
            # DB セッションを準備
            if db is None:
                db = next(get_db())
            # 議事録の確認
            meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
            if not meeting:
                raise Exception("議事録が見つかりません")
            
            # 1. 音声チャンクの文字起こし
            transcription_text = await self._transcribe_chunks(meeting_id, db)
            
            # 文字起こし結果が空の場合はダミー生成せずにエラー扱い
            if not transcription_text or not transcription_text.strip():
                print("DEBUG: 文字起こしデータが空です。要約を中止します。")
                raise Exception("文字起こしデータが空です")
            
            # 2. 要約の生成
            summary = await self._generate_summary(transcription_text)
            
            # 3. Google Driveへの保存
            file_url = await self._save_to_drive(meeting_id, summary)
            
            # 4. データベースの更新
            await self._update_meeting_status(meeting_id, "completed", file_url, db)
            
            return file_url
        
        except Exception as e:
            await self._update_meeting_status(meeting_id, "error")
            raise Exception(f"議事録の処理に失敗しました: {str(e)}")
    
    async def _transcribe_chunks(self, meeting_id: int, db: Session) -> str:
        """音声チャンクの文字起こし"""
        transcriptions = []
        
        # チャンクファイルの取得（デバッグ用に条件を緩和）
        chunks = db.query(AudioChunk).filter(
            AudioChunk.meeting_id == meeting_id
        ).order_by(AudioChunk.chunk_number).all()
        
        # uploadedステータスのチャンクのみをフィルタ
        uploaded_chunks = [chunk for chunk in chunks if chunk.status == "uploaded"]
        print(f"DEBUG: uploadedステータスのチャンク数: {len(uploaded_chunks)}")
        
        chunks = uploaded_chunks
        
        print(f"DEBUG: 文字起こし対象チャンク数: {len(chunks)}")
        
        # デバッグ用：全チャンクを確認
        all_chunks = db.query(AudioChunk).filter(
            AudioChunk.meeting_id == meeting_id
        ).all()
        print(f"DEBUG: 全チャンク数: {len(all_chunks)}")
        for chunk in all_chunks:
            print(f"DEBUG: チャンク - ID: {chunk.id}, 番号: {chunk.chunk_number}, ステータス: {chunk.status}, ファイル名: {chunk.filename}")
        
        total_whisper_tokens = 0
        
        for chunk in chunks:
            try:
                file_path = os.path.join(self.upload_dir, chunk.filename)
                print(f"DEBUG: チャンクファイル確認 - {chunk.filename}: {os.path.exists(file_path)}")
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"DEBUG: ファイルサイズ: {file_size} bytes")
                    if file_size == 0:
                        print(f"DEBUG: ファイルサイズが0です: {chunk.filename}")
                        continue
                    
                    # 通常の文字起こし
                    transcription_text = await self.whisper_service.transcribe(file_path)
                    if transcription_text and transcription_text.strip():
                        transcriptions.append(transcription_text)
                        # チャンクに転写を保存
                        chunk.transcription = transcription_text
                    
                    # トークン数を更新
                    if transcription_text:
                        total_whisper_tokens += len(transcription_text.split())
                    
                    # チャンクのステータスを更新
                    chunk.status = "transcribed"
                    db.commit()
                    print(f"DEBUG: 文字起こし完了: {chunk.filename}")
                else:
                    print(f"ファイルが見つかりません: {chunk.filename}")
            except Exception as e:
                print(f"チャンク {chunk.filename} の文字起こしに失敗: {str(e)}")
                chunk.status = "error"
                db.commit()
        
        print(f"DEBUG: 文字起こし完了数: {len(transcriptions)}")
        
        # 議事録のWhisperトークン数・全文転写を更新
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.whisper_tokens = total_whisper_tokens
            full_transcript = "\n".join(transcriptions)
            meeting.transcript = full_transcript
            db.commit()
        
        # 全文字起こしを結合
        return "\n".join(transcriptions)
    
    async def _generate_summary(self, transcription_text: str) -> str:
        """文字起こしから要約を生成"""
        try:
            print(f"DEBUG: 要約生成開始 - 文字数: {len(transcription_text)}")
            # ChatGPTで要約
            summary = await self.summary_service.generate_summary(transcription_text)
            print(f"DEBUG: 要約生成完了 - 文字数: {len(summary)}")
            
            return summary
        
        except Exception as e:
            print(f"DEBUG: 要約生成エラー - {str(e)}")
            raise Exception(f"要約の生成に失敗しました: {str(e)}")
    
    async def _save_to_drive(self, meeting_id: int, summary: str) -> str:
        """要約をデータベースに保存"""
        try:
            print(f"DEBUG: 要約データベース保存開始 - meeting_id: {meeting_id}")
            
            # データベースに要約を保存
            db = next(get_db())
            meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
            
            if meeting:
                meeting.summary = summary
                db.commit()
                print(f"DEBUG: 要約データベース保存完了 - meeting_id: {meeting_id}")
                print(f"DEBUG: 要約文字数: {len(summary)} 文字")
                return f"/api/recording/summary/{meeting_id}"
            else:
                raise Exception(f"会議ID {meeting_id} が見つかりません")
        
        except Exception as e:
            print(f"DEBUG: データベース保存エラー - {str(e)}")
            import traceback
            print(f"DEBUG: エラー詳細: {traceback.format_exc()}")
            raise Exception(f"要約の保存に失敗しました: {str(e)}")
    
    async def _update_meeting_status(self, meeting_id: int, status: str, file_url: str = None, db: Session = None):
        """議事録のステータスを更新"""
        try:
            if db is None:
                db = next(get_db())
            
            meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
            if meeting:
                meeting.status = status
                if file_url:
                    meeting.drive_file_url = file_url
                db.commit()
        
        except Exception as e:
            print(f"議事録ステータスの更新に失敗: {str(e)}")
    
    def get_chunk_files(self, meeting_id: int) -> List[str]:
        """会議IDに対応するチャンクファイルを取得"""
        try:
            chunk_files = []
            for filename in os.listdir(self.upload_dir):
                if filename.startswith(f"meeting_{meeting_id}_chunk_"):
                    chunk_files.append(filename)
            
            # チャンク番号でソート
            chunk_files.sort(key=lambda x: int(x.split('_')[3]))
            return chunk_files
        
        except Exception as e:
            print(f"チャンクファイルの取得に失敗: {str(e)}")
            return []
    
    def cleanup_old_files(self, days: int = 7):
        """古いファイルの削除"""
        try:
            current_time = datetime.now()
            deleted_count = 0
            
            for filename in os.listdir(self.upload_dir):
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if (current_time - file_time).days > days:
                        os.remove(file_path)
                        deleted_count += 1
                        print(f"古いファイルを削除: {filename}")
            
            print(f"合計 {deleted_count} 個のファイルを削除しました")
            return deleted_count
        
        except Exception as e:
            print(f"ファイルクリーンアップに失敗: {str(e)}")
            return 0
    
    def get_storage_usage(self) -> dict:
        """ストレージ使用量を取得"""
        try:
            total_size = 0
            file_count = 0
            
            # アップロードディレクトリが存在しない場合は作成
            if not os.path.exists(self.upload_dir):
                os.makedirs(self.upload_dir, exist_ok=True)
            
            for filename in os.listdir(self.upload_dir):
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "upload_dir": self.upload_dir
            }
        
        except Exception as e:
            print(f"ストレージ使用量の取得に失敗: {str(e)}")
            return {
                "total_size_bytes": 0, 
                "total_size_mb": 0, 
                "file_count": 0,
                "upload_dir": self.upload_dir,
                "error": str(e)
            } 