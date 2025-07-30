import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class SummaryService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception('OPENAI_API_KEYが.envに設定されていません')
        # APIキーから改行文字を除去
        api_key = api_key.strip()
        self.client = OpenAI(api_key=api_key)
    
    async def generate_summary(self, transcript: str, participants: list = None) -> str:
        """転写テキストから要約を生成"""
        try:
            print(f"要約生成開始 - 転写テキスト長: {len(transcript)}文字")
            
            # 参加者情報を含むプロンプトを作成
            participant_info = ""
            if participants and len(participants) > 0:
                participant_info = f"\n参加者: {', '.join(participants)}"
            
            prompt = f"""以下の会議の転写テキストを要約してください。

{participant_info}

転写テキスト:
{transcript}

以下の形式で要約してください：

## 会議概要
- 主要な議題と決定事項
- 重要なポイント

## アクションアイテム
- 担当者と期限を含む具体的なタスク

## 次回の議題
- 次回会議で取り上げる予定の項目

要約は簡潔で実用的なものにしてください。"""

            print(f"ChatGPT API呼び出し開始...")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは会議の要約を専門とするアシスタントです。転写テキストから重要な情報を抽出し、構造化された要約を作成してください。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            print(f"ChatGPT API応答: {response}")
            
            summary = response.choices[0].message.content
            print(f"生成された要約: {summary}")
            
            return summary
            
        except Exception as e:
            print(f"要約生成中にエラーが発生: {str(e)}")
            import traceback
            print(f"詳細エラー: {traceback.format_exc()}")
            raise Exception(f"要約生成に失敗しました: {str(e)}")
    
    async def generate_speaker_summary(self, speakers_data: dict) -> str:
        """話者別の要約を生成"""
        try:
            print(f"話者別要約生成開始 - 話者数: {len(speakers_data.get('speakers', {}))}")
            
            # 話者データを構造化
            speaker_summaries = []
            for speaker_id, speaker_info in speakers_data.get('speakers', {}).items():
                utterances = speaker_info.get('utterances', [])
                if utterances:
                    # 話者の発言を結合
                    speaker_text = " ".join([utt.get('text', '') for utt in utterances])
                    speaker_name = speaker_info.get('name', f"話者{speaker_id}")
                    
                    speaker_summaries.append(f"## {speaker_name}\n{speaker_text}\n")
            
            if not speaker_summaries:
                return "話者データが見つかりませんでした。"
            
            combined_text = "\n".join(speaker_summaries)
            
            prompt = f"""以下の話者別の発言内容を要約してください：

{combined_text}

各話者の主要な発言内容と貢献度を簡潔にまとめてください。"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは会議の話者別分析を専門とするアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            print(f"話者別要約生成完了: {summary}")
            
            return summary
            
        except Exception as e:
            print(f"話者別要約生成中にエラーが発生: {str(e)}")
            import traceback
            print(f"詳細エラー: {traceback.format_exc()}")
            raise Exception(f"話者別要約生成に失敗しました: {str(e)}") 