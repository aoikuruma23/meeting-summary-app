-- Supabase移行用のテーブル作成SQL
-- このファイルをSupabaseのSQL Editorで実行してください

-- ユーザーテーブル
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR,
    is_active VARCHAR DEFAULT 'active',
    name VARCHAR,
    profile_picture VARCHAR,
    is_premium VARCHAR DEFAULT 'false',
    usage_count INTEGER DEFAULT 0,
    trial_start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    auth_provider VARCHAR,
    google_id VARCHAR,
    line_user_id VARCHAR,
    stripe_customer_id VARCHAR,
    stripe_subscription_id VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_users_line_user_id ON users(line_user_id);

-- ミーティングテーブル
CREATE TABLE IF NOT EXISTS meetings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR,
    filename VARCHAR,
    drive_file_id VARCHAR,
    drive_file_url VARCHAR,
    status VARCHAR DEFAULT 'recording',
    whisper_tokens INTEGER DEFAULT 0,
    gpt_tokens INTEGER DEFAULT 0,
    summary TEXT,
    transcript TEXT,
    participants TEXT,
    max_duration INTEGER,
    scheduled_duration INTEGER,
    actual_duration INTEGER,
    topic_count INTEGER DEFAULT 0,
    completed_topics INTEGER DEFAULT 0,
    decision_count INTEGER DEFAULT 0,
    action_item_count INTEGER DEFAULT 0,
    participant_count INTEGER DEFAULT 0,
    efficiency_score FLOAT,
    is_encrypted VARCHAR DEFAULT 'false',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_meetings_user_id ON meetings(user_id);
CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status);
CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings(created_at);

-- オーディオチャンクテーブル
CREATE TABLE IF NOT EXISTS audio_chunks (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id),
    chunk_number INTEGER,
    filename VARCHAR,
    transcription TEXT,
    status VARCHAR DEFAULT 'uploaded',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_audio_chunks_meeting_id ON audio_chunks(meeting_id);
CREATE INDEX IF NOT EXISTS idx_audio_chunks_chunk_number ON audio_chunks(chunk_number);

-- スピーカーテーブル
CREATE TABLE IF NOT EXISTS speakers (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id),
    speaker_id VARCHAR,
    name VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_speakers_meeting_id ON speakers(meeting_id);
CREATE INDEX IF NOT EXISTS idx_speakers_speaker_id ON speakers(speaker_id);

-- 発言テーブル
CREATE TABLE IF NOT EXISTS utterances (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id),
    speaker_id INTEGER REFERENCES speakers(id),
    start_time FLOAT,
    end_time FLOAT,
    text TEXT,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_utterances_meeting_id ON utterances(meeting_id);
CREATE INDEX IF NOT EXISTS idx_utterances_speaker_id ON utterances(speaker_id);
CREATE INDEX IF NOT EXISTS idx_utterances_start_time ON utterances(start_time);

-- 更新時刻の自動更新用トリガー関数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- トリガー作成
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meetings_updated_at BEFORE UPDATE ON meetings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS（Row Level Security）の設定
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;
ALTER TABLE audio_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE speakers ENABLE ROW LEVEL SECURITY;
ALTER TABLE utterances ENABLE ROW LEVEL SECURITY;

-- 基本的なRLSポリシー（必要に応じて調整）
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Users can view own meetings" ON meetings
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own meetings" ON meetings
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own meetings" ON meetings
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- 完了メッセージ
SELECT 'Supabase移行用テーブル作成完了' as status;
