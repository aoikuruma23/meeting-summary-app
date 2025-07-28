import sqlite3
import os

def add_stripe_fields():
    """Stripe関連フィールドを追加"""
    db_path = "meeting_summary.db"
    
    if not os.path.exists(db_path):
        print("データベースファイルが見つかりません")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # テーブル構造を確認
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # stripe_customer_idフィールドを追加
        if "stripe_customer_id" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN stripe_customer_id TEXT")
            print("stripe_customer_idフィールドを追加しました")
        else:
            print("stripe_customer_idフィールドは既に存在します")
        
        # stripe_subscription_idフィールドを追加
        if "stripe_subscription_id" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN stripe_subscription_id TEXT")
            print("stripe_subscription_idフィールドを追加しました")
        else:
            print("stripe_subscription_idフィールドは既に存在します")
        
        conn.commit()
        print("Stripe関連フィールドの追加が完了しました")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    add_stripe_fields() 