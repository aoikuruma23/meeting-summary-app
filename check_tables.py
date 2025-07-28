print("=== DBテーブル一覧取得開始 ===")
import sqlite3
conn = sqlite3.connect("backend/meeting_summary.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("テーブル一覧:", tables)
conn.close()
print("=== 終了 ===") 