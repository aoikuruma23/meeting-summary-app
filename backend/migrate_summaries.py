#!/usr/bin/env python3
"""
既存の要約ファイルをデータベースに移行するスクリプト
"""

import os
import glob
from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.models.meeting import Meeting

def migrate_summaries_to_database():
    """要約ファイルをデータベースに移行"""
    try:
        print("=== 要約ファイルのデータベース移行を開始 ===")
        
        # summariesディレクトリのパス
        current_dir = os.path.dirname(os.path.abspath(__file__))
        summaries_dir = os.path.join(current_dir, "summaries")
        
        if not os.path.exists(summaries_dir):
            print(f"summariesディレクトリが存在しません: {summaries_dir}")
            return
        
        # 要約ファイルを検索
        pattern = os.path.join(summaries_dir, "*_議事録_*.txt")
        summary_files = glob.glob(pattern)
        
        print(f"見つかった要約ファイル数: {len(summary_files)}")
        
        if not summary_files:
            print("移行する要約ファイルが見つかりません")
            return
        
        # データベース接続
        db = next(get_db())
        
        migrated_count = 0
        
        for file_path in summary_files:
            try:
                # ファイル名からmeeting_idを抽出
                filename = os.path.basename(file_path)
                if "_議事録_" in filename:
                    meeting_id_str = filename.split("_議事録_")[1].replace(".txt", "")
                    meeting_id = int(meeting_id_str)
                    
                    # ファイル内容を読み込み
                    with open(file_path, 'r', encoding='utf-8') as f:
                        summary_content = f.read()
                    
                    # データベースのmeetingを検索
                    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
                    
                    if meeting:
                        # 既にsummaryが設定されている場合はスキップ
                        if meeting.summary:
                            print(f"会議ID {meeting_id}: 既に要約が設定されています")
                            continue
                        
                        # 要約をデータベースに保存
                        meeting.summary = summary_content
                        db.commit()
                        
                        print(f"会議ID {meeting_id}: 要約を移行しました ({len(summary_content)} 文字)")
                        migrated_count += 1
                    else:
                        print(f"会議ID {meeting_id}: データベースに会議が見つかりません")
                
            except Exception as e:
                print(f"ファイル {file_path} の移行に失敗: {str(e)}")
                continue
        
        print(f"=== 移行完了: {migrated_count} 件の要約を移行しました ===")
        
    except Exception as e:
        print(f"移行中にエラーが発生: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_summaries_to_database() 