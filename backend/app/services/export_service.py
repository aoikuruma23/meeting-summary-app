import os
import json
from datetime import datetime, timezone, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from app.models.meeting import Meeting

class ExportService:
    def __init__(self):
        self.export_dir = os.path.join("uploads", "exports")
        os.makedirs(self.export_dir, exist_ok=True)
    
    def jst_now(self):
        """日本時間（JST）の現在時刻を返す"""
        jst = timezone(timedelta(hours=9))
        return datetime.now(jst)
    
    def format_jst_datetime(self, dt):
        """日本時間でフォーマット"""
        if dt:
            # データベースの時間がUTCの場合、JSTに変換
            if dt.tzinfo is None:
                # タイムゾーン情報がない場合はUTCとして扱い、JSTに変換
                utc_time = dt.replace(tzinfo=timezone.utc)
                jst_time = utc_time.astimezone(timezone(timedelta(hours=9)))
            else:
                # 既にタイムゾーン情報がある場合はJSTに変換
                jst_time = dt.astimezone(timezone(timedelta(hours=9)))
            
            return jst_time.strftime('%Y年%m月%d日 %H:%M')
        else:
            # 現在時刻を使用
            return self.jst_now().strftime('%Y年%m月%d日 %H:%M')
    
    def safe_text(self, text):
        """テキストを安全に処理"""
        if not text:
            return ""
        # 改行文字を削除
        text = text.replace('\n', ' ')
        # 特殊文字をエスケープ
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text
    
    async def export_to_pdf(self, meeting) -> str:
        """要約をPDF形式でエクスポート"""
        try:
            # ファイル名を生成
            timestamp = self.jst_now().strftime("%Y%m%d_%H%M%S")
            filename = f"meeting_{meeting.id}_{timestamp}.pdf"
            file_path = os.path.join(self.export_dir, filename)
            
            # PDFドキュメントを作成
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # スタイルを定義
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # 中央揃え
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12
            )
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            )
            
            # タイトルを追加
            story.append(Paragraph(self.safe_text("議事録要約"), title_style))
            story.append(Spacer(1, 20))
            
            # 会議情報を追加
            story.append(Paragraph(self.safe_text(f"会議タイトル: {meeting.title}"), heading_style))
            story.append(Paragraph(self.safe_text(f"作成日時: {self.format_jst_datetime(meeting.created_at)}"), normal_style))
            story.append(Paragraph(self.safe_text(f"議事録ID: {meeting.id}"), normal_style))
            story.append(Spacer(1, 20))
            
            # 要約内容を追加
            story.append(Paragraph(self.safe_text("要約内容"), heading_style))
            
            # 要約を段落に分割して追加
            paragraphs = meeting.summary.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    story.append(Paragraph(self.safe_text(paragraph.strip()), normal_style))
                    story.append(Spacer(1, 6))
            
            # PDFを生成
            doc.build(story)
            
            return file_path
            
        except Exception as e:
            print(f"ERROR: PDFエクスポート失敗: {str(e)}")
            raise Exception(f"PDFエクスポートに失敗しました: {str(e)}")
    
    async def export_to_docx(self, meeting) -> str:
        """要約をWord形式でエクスポート"""
        try:
            # ファイル名を生成
            timestamp = self.jst_now().strftime("%Y%m%d_%H%M%S")
            filename = f"meeting_{meeting.id}_{timestamp}.docx"
            file_path = os.path.join(self.export_dir, filename)
            
            # Wordドキュメントを作成
            doc = Document()
            
            # タイトルを追加
            title = doc.add_heading("議事録要約", 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # 会議情報を追加
            doc.add_heading("会議情報", level=1)
            doc.add_paragraph(f"会議タイトル: {meeting.title}")
            doc.add_paragraph(f"作成日時: {self.format_jst_datetime(meeting.created_at)}")
            doc.add_paragraph(f"議事録ID: {meeting.id}")
            
            # 要約内容を追加
            doc.add_heading("要約内容", level=1)
            
            # 要約を段落に分割して追加
            paragraphs = meeting.summary.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    doc.add_paragraph(paragraph.strip())
            
            # Wordファイルを保存
            doc.save(file_path)
            
            return file_path
            
        except Exception as e:
            print(f"ERROR: Wordエクスポート失敗: {str(e)}")
            raise Exception(f"Wordエクスポートに失敗しました: {str(e)}")
    
    def cleanup_old_exports(self, max_age_hours: int = 24):
        """古いエクスポートファイルを削除"""
        try:
            current_time = datetime.now()
            for filename in os.listdir(self.export_dir):
                file_path = os.path.join(self.export_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if (current_time - file_time).total_seconds() > max_age_hours * 3600:
                        os.remove(file_path)
                        print(f"古いエクスポートファイルを削除: {filename}")
        except Exception as e:
            print(f"エクスポートファイルのクリーンアップに失敗: {str(e)}") 