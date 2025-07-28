import sqlite3
import os
from datetime import datetime

def add_max_duration_column():
    """meetingsテーブルにmax_durationカラムを追加"""
    
    # データベースファイルのパス
    db_path = os.path.join(os.path.dirname(__file__), '..', 'meeting_summary.db')
    
    try:
        # データベースに接続
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # max_durationカラムが存在するかチェック
        cursor.execute("PRAGMA table_info(meetings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'max_duration' not in columns:
            # max_durationカラムを追加
            cursor.execute("""
                ALTER TABLE meetings 
                ADD COLUMN max_duration INTEGER
            """)
            
            print(f"[{datetime.now()}] max_durationカラムを追加しました")
        else:
            print(f"[{datetime.now()}] max_durationカラムは既に存在します")
        
        # 変更をコミット
        conn.commit()
        print(f"[{datetime.now()}] マイグレーション完了")
        
    except Exception as e:
        print(f"[{datetime.now()}] エラー: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_max_duration_column() 