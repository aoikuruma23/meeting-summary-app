import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from app.core.config import settings

load_dotenv()

class SummaryService:
    def __init__(self):
        # 設定からAPIキーを取得（環境差異なく統一）
        api_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception('OPENAI_API_KEYが設定されていません')
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
            
            prompt = f"""以下の会議の転写テキストを日本語で厳密に要約してください。転写に含まれない情報は追加しないでください（仮定・推測・創作は禁止）。

{participant_info}

転写テキスト:
{transcript}

出力要件（重要）:
- 出力はMarkdownで、日本語。
- 各項目は具体的・網羅的に。冗長な言い換えは避け、実際の内容を箇条書きで丁寧に記述。
- 目安の長さ: 全体で800〜1500文字（内容が多い場合は上限2000文字まで）。
- 転写にない情報は書かず、情報が不足する箇所は「記載なし」と明示。

出力フォーマット:
## 会議概要（300〜500文字）
- 主題・背景・目的を具体的に要約
- 重要な論点を簡潔に列挙（実際の内容のみ）

## 決定事項（最低5項目が目安。少ない場合はある分だけ）
- 何を／なぜ／どうする（条件や前提があれば併記）

## 議論の詳細（論点ごとに箇条書き：各論点2〜4行）
- 論点A: 主要な主張・反論・合意点
- 論点B: 主要な主張・反論・合意点

## アクションアイテム（担当・期限・具体内容。情報が無ければ「未指定」）
- 担当: ／期限: ／内容:

## 次回の議題／持ち越し課題
- 実際に挙がったもののみ。無ければ「記載なし」。

厳守事項: 事実は転写テキストのみに基づき、憶測を入れない。"""

            print(f"ChatGPT API呼び出し開始...")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは会議の要約を専門とする日本語アシスタントです。転写にない情報を付け加えず、厳密に事実のみを構造化して出力します。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.15
            )
            
            # 必要以上の詳細ログは出さない（情報漏洩防止）
            usage = getattr(response, 'usage', None)
            if usage:
                print(f"DEBUG: Chat usage - prompt_tokens={getattr(usage, 'prompt_tokens', 'n/a')}, completion_tokens={getattr(usage, 'completion_tokens', 'n/a')}, total_tokens={getattr(usage, 'total_tokens', 'n/a')}")
            
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