from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    filename = Column(String)
    drive_file_id = Column(String, nullable=True)
    drive_file_url = Column(String, nullable=True)
    
    # 処理状況
    status = Column(String, default="recording")  # recording, processing, completed, error
    whisper_tokens = Column(Integer, default=0)
    gpt_tokens = Column(Integer, default=0)
    
    # 要約・転写データ
    summary = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    participants = Column(Text, nullable=True)  # JSON文字列で参加者名を保存
    
    # 録音時間制限
    max_duration = Column(Integer, nullable=True)        # 最大録音時間（分）
    
    # 生産性関連
    scheduled_duration = Column(Integer, nullable=True)  # 予定時間（分）
    actual_duration = Column(Integer, nullable=True)     # 実際の時間（分）
    topic_count = Column(Integer, default=0)
    completed_topics = Column(Integer, default=0)
    decision_count = Column(Integer, default=0)
    action_item_count = Column(Integer, default=0)
    participant_count = Column(Integer, default=0)
    efficiency_score = Column(Float, nullable=True)
    
    # 暗号化
    is_encrypted = Column(String, default="false")
    
    # メタデータ
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # リレーション
    # user = relationship("User", back_populates="meetings")  # 一時的にコメントアウト
    chunks = relationship("AudioChunk", back_populates="meeting")
    speakers = relationship("Speaker", back_populates="meeting")
    utterances = relationship("Utterance", back_populates="meeting")
    
    def __repr__(self):
        return f"<Meeting(id={self.id}, title={self.title}, status={self.status})>"

class AudioChunk(Base):
    __tablename__ = "audio_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    chunk_number = Column(Integer)
    filename = Column(String)
    transcription = Column(Text, nullable=True)
    
    # 処理状況
    status = Column(String, default="uploaded")  # uploaded, transcribed, error
    
    # メタデータ
    created_at = Column(DateTime, default=func.now())
    
    # リレーション
    meeting = relationship("Meeting", back_populates="chunks")
    
    def __repr__(self):
        return f"<AudioChunk(id={self.id}, meeting_id={self.meeting_id}, chunk_number={self.chunk_number})>"

class Speaker(Base):
    __tablename__ = "speakers"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    speaker_id = Column(String)  # Whisperが生成する話者ID
    name = Column(String, nullable=True)  # ユーザーが設定する名前
    
    # メタデータ
    created_at = Column(DateTime, default=func.now())
    
    # リレーション
    meeting = relationship("Meeting", back_populates="speakers")
    utterances = relationship("Utterance", back_populates="speaker")
    
    def __repr__(self):
        return f"<Speaker(id={self.id}, speaker_id={self.speaker_id}, name={self.name})>"

class Utterance(Base):
    __tablename__ = "utterances"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    speaker_id = Column(Integer, ForeignKey("speakers.id"))
    start_time = Column(Float)  # 開始時間（秒）
    end_time = Column(Float)    # 終了時間（秒）
    text = Column(Text)         # 発言内容
    confidence = Column(Float, nullable=True)  # 信頼度
    
    # メタデータ
    created_at = Column(DateTime, default=func.now())
    
    # リレーション
    meeting = relationship("Meeting", back_populates="utterances")
    speaker = relationship("Speaker", back_populates="utterances")
    
    def __repr__(self):
        return f"<Utterance(id={self.id}, speaker_id={self.speaker_id}, text={self.text[:50]}...)>" 