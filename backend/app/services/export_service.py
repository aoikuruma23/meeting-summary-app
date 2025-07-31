import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from app.core.config import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.colors import black, blue
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import base64

class ExportService:
    def __init__(self):
        self.export_dir = os.path.join(settings.UPLOAD_DIR, "exports")
        os.makedirs(self.export_dir, exist_ok=True)
        
        # 日本語フォントの設定
        font_name = self._create_japanese_font()
        
        # スタイルの設定
        styles = getSampleStyleSheet()
        
        # カスタムスタイルの作成
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName=font_name
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            fontName=font_name
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            fontName=font_name
        )
        """日本語フォントを登録"""
        font_registered = False
        
        # 利用可能なフォントを確認
        available_fonts = pdfmetrics.getRegisteredFontNames()
        print(f"利用可能なフォント: {available_fonts}")
        
        # 日本語フォントの優先順位
        japanese_fonts = ['JapaneseFont', 'HeiseiMin-W3', 'HeiseiKakuGo-W5', 'HeiseiKakuGo-W3']
        font_name = 'Helvetica'  # デフォルト
        
        for font in japanese_fonts:
            if font in available_fonts:
                font_name = font
                print(f"日本語フォントを使用: {font}")
                break
        
        if font_name == 'Helvetica':
            print("警告: 日本語フォントが利用できません。Helveticaを使用します。")
        
        return font_name
    
    def _create_japanese_font(self):
        """日本語フォントを直接作成"""
        try:
            # 基本的な日本語フォントを試行
            font_name = self._register_japanese_font()
            
            # フォントが見つからない場合、UnicodeCIDFontを使用
            if font_name == 'Helvetica':
                try:
                    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
                    font_name = 'HeiseiMin-W3'
                    print("UnicodeCIDFontを登録しました: HeiseiMin-W3")
                except Exception as e:
                    print(f"UnicodeCIDFont登録失敗: {str(e)}")
                    try:
                        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
                        font_name = 'HeiseiKakuGo-W5'
                        print("UnicodeCIDFontを登録しました: HeiseiKakuGo-W5")
                    except Exception as e:
                        print(f"UnicodeCIDFont登録失敗: {str(e)}")
                        font_name = 'Helvetica'
            
            return font_name
        except Exception as e:
            print(f"フォント作成エラー: {str(e)}")
            return 'Helvetica'
    
    def export_to_pdf(self, meeting_title: str, summary_content: str, meeting_id: int) -> str:
        """要約をPDF形式でエクスポート"""
        try:
            # ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meeting_{meeting_id}_{timestamp}.pdf"
            file_path = os.path.join(self.export_dir, filename)
            
            # PDFドキュメントを作成
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # スタイルを設定
            styles = getSampleStyleSheet()
            
            # フォント名を決定
            available_fonts = pdfmetrics.getRegisteredFontNames()
            print(f"利用可能なフォント: {available_fonts}")
            
            # 日本語フォントの優先順位
            japanese_fonts = ['JapaneseFont', 'HeiseiMin-W3', 'HeiseiKakuGo-W5', 'HeiseiKakuGo-W3']
            font_name = 'Helvetica'  # デフォルト
            
            for font in japanese_fonts:
                if font in available_fonts:
                    font_name = font
                    print(f"日本語フォントを使用: {font}")
                    break
            
            if font_name == 'Helvetica':
                print("警告: 日本語フォントが利用できません。Helveticaを使用します。")
            
            # 日本語テキストのエンコーディング処理
            def safe_text(text):
                """日本語テキストを安全に処理"""
                try:
                    # UTF-8でエンコードしてからデコード
                    return text.encode('utf-8').decode('utf-8')
                except:
                    return text
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=font_name,
                fontSize=18,
                spaceAfter=30,
                alignment=1  # 中央揃え
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontName=font_name,
                fontSize=14,
                spaceAfter=12,
                spaceBefore=12
            )
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=11,
                spaceAfter=6,
                leading=14
            )
            
            # タイトルを追加
            story.append(Paragraph(safe_text("議事録要約"), title_style))
            story.append(Spacer(1, 20))
            
            # 会議情報を追加
            story.append(Paragraph(safe_text(f"会議タイトル: {meeting_title}"), heading_style))
            story.append(Paragraph(safe_text(f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}"), normal_style))
            story.append(Paragraph(safe_text(f"議事録ID: {meeting_id}"), normal_style))
            story.append(Spacer(1, 20))
            
            # 要約内容を追加
            story.append(Paragraph(safe_text("要約内容"), heading_style))
            
            # 要約を段落に分割して追加
            paragraphs = summary_content.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    story.append(Paragraph(safe_text(paragraph.strip()), normal_style))
                    story.append(Spacer(1, 6))
            
            # PDFを生成
            doc.build(story)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"PDFエクスポートに失敗しました: {str(e)}")
    
    def export_to_word(self, meeting_title: str, summary_content: str, meeting_id: int) -> str:
        """要約をWord形式でエクスポート"""
        try:
            # ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meeting_{meeting_id}_{timestamp}.docx"
            file_path = os.path.join(self.export_dir, filename)
            
            # Wordドキュメントを作成
            doc = Document()
            
            # タイトルを追加
            title = doc.add_heading("議事録要約", 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # 会議情報を追加
            doc.add_heading("会議情報", level=1)
            doc.add_paragraph(f"会議タイトル: {meeting_title}")
            doc.add_paragraph(f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
            doc.add_paragraph(f"議事録ID: {meeting_id}")
            
            # 要約内容を追加
            doc.add_heading("要約内容", level=1)
            
            # 要約を段落に分割して追加
            paragraphs = summary_content.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    doc.add_paragraph(paragraph.strip())
            
            # Wordファイルを保存
            doc.save(file_path)
            
            return file_path
            
        except Exception as e:
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