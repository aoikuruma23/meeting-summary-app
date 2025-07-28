print("=== 手動テーブル作成開始 ===")

# backendディレクトリに移動
import os
os.chdir("backend")

# データベース設定をimport
from app.core.config import settings
from app.core.database import Base, engine

# 全モデルをimport
from app.models import meeting, user

print("全モデルをimportしました")

# テーブルを作成
Base.metadata.create_all(bind=engine)

print("テーブル作成完了")

# テーブル一覧を確認
import sqlite3
conn = sqlite3.connect("meeting_summary.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("テーブル一覧:", tables)
conn.close()

print("=== 終了 ===") 