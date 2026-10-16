import os
import re
import html
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, Image, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# -------------------------------------------------------------------------
# FONT REGISTRATION
# -------------------------------------------------------------------------
FONTS_AVAILABLE = False
try:
    if os.path.exists('C:/Windows/Fonts/segoeui.ttf'):
        pdfmetrics.registerFont(TTFont('SegoeUI', 'C:/Windows/Fonts/segoeui.ttf'))
        pdfmetrics.registerFont(TTFont('SegoeUI-Bold', 'C:/Windows/Fonts/segoeuib.ttf'))
        pdfmetrics.registerFont(TTFont('SegoeUI-Italic', 'C:/Windows/Fonts/segoeuii.ttf'))
        pdfmetrics.registerFont(TTFont('Consolas', 'C:/Windows/Fonts/consola.ttf'))
        pdfmetrics.registerFont(TTFont('Consolas-Bold', 'C:/Windows/Fonts/consolab.ttf'))
        FONTS_AVAILABLE = True
except Exception as e:
    print(f"Font registration warning: {e}")

FONT_MAIN = 'SegoeUI' if FONTS_AVAILABLE else 'Helvetica'
FONT_BOLD = 'SegoeUI-Bold' if FONTS_AVAILABLE else 'Helvetica-Bold'
FONT_ITALIC = 'SegoeUI-Italic' if FONTS_AVAILABLE else 'Helvetica-Oblique'
FONT_MONO = 'Consolas' if FONTS_AVAILABLE else 'Courier'
FONT_MONO_BOLD = 'Consolas-Bold' if FONTS_AVAILABLE else 'Courier-Bold'

# -------------------------------------------------------------------------
# COLOR PALETTE (Fintech Lavender & Warm Minimalist)
# -------------------------------------------------------------------------
PRIMARY = colors.HexColor('#8A63F4')        # Vibrant Lavender Accent
PRIMARY_DARK = colors.HexColor('#5E35B1')   # Deep Indigo / Heading Purple
PRIMARY_LIGHT = colors.HexColor('#B9A0F5')  # Soft Accent
LAVENDER_BG = colors.HexColor('#F5EEFE')    # Soft Lavender Card Fill
LAVENDER_BORDER = colors.HexColor('#D1C4E9')

TEXT_DARK = colors.HexColor('#20201F')      # Charcoal Primary Text
TEXT_MUTED = colors.HexColor('#77736F')     # Muted Grey Text
CANVAS_BG = colors.HexColor('#F8F3EF')      # Warm Off-white Canvas
SURFACE_WHITE = colors.HexColor('#FFFFFF')  # Card Surface
BORDER_LIGHT = colors.HexColor('#ECE8E5')   # Subtle Border
CODE_BG = colors.HexColor('#F4F0EB')        # Code Block Background
CODE_TEXT = colors.HexColor('#2E2A28')      # Code Block Text

GREEN_ACCENT = colors.HexColor('#059669')   # Success Green
GREEN_BG = colors.HexColor('#ECFDF5')
AMBER_ACCENT = colors.HexColor('#D97706')   # Warning Amber
AMBER_BG = colors.HexColor('#FFFBEB')
RED_ACCENT = colors.HexColor('#DC2626')     # Critical Red
RED_BG = colors.HexColor('#FEF2F2')

# Printable width on Letter (8.5 x 11 inches) with 40pt margins = 612 - 80 = 532 pt
PAGE_WIDTH = 612
PAGE_HEIGHT = 792
MARGIN_LEFT = 40
MARGIN_RIGHT = 40
MARGIN_TOP = 48
MARGIN_BOTTOM = 48
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT # 532 pt

# -------------------------------------------------------------------------
# XML ESCAPE HELPER FOR REPORTLAB
# -------------------------------------------------------------------------
def escape_xml(text: str) -> str:
    """Escapes raw text while preserving formatting tags (b, i, font, u, br) and converting code tags."""
    if not text:
        return ""
    # Convert inline code tags to styled font tags
    text = re.sub(r'<code>(.*?)</code>', rf'<font face="{FONT_MONO}" color="#5E35B1">\1</font>', text)
    # Split by allowed formatting tags
    tokens = re.split(r'(</?[biu]>|</?font[^>]*>|<br\s*/?>|&[a-zA-Z]+;)', text)
    res = []
    for t in tokens:
        if not t:
            continue
        if re.match(r'^</?[biu]>$', t) or re.match(r'^</?font[^>]*>$', t) or re.match(r'^<br\s*/?>$', t) or re.match(r'^&[a-zA-Z]+;$', t):
            res.append(t)
        else:
            t_escaped = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            res.append(t_escaped)
    return ''.join(res)

# -------------------------------------------------------------------------
# NUMBERED CANVAS FOR TWO-PASS "PAGE X OF Y"
# -------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Page 1 is the cover page: skip header and footer
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont(FONT_MAIN, 8)
        self.setFillColor(TEXT_MUTED)

        # Running Header
        self.drawString(MARGIN_LEFT, PAGE_HEIGHT - 32, "UPI Transaction Intelligence System — Complete Hinglish Technical Guide")
        self.setStrokeColor(BORDER_LIGHT)
        self.setLineWidth(0.75)
        self.line(MARGIN_LEFT, PAGE_HEIGHT - 38, PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 38)

        # Running Footer
        self.line(MARGIN_LEFT, 36, PAGE_WIDTH - MARGIN_RIGHT, 36)
        self.drawString(MARGIN_LEFT, 24, "Academic & Fintech Industry Guide • PhonePe / Razorpay / Visa Reference")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, 24, page_str)
        self.restoreState()

# -------------------------------------------------------------------------
# STYLESHEET SETUP
# -------------------------------------------------------------------------
def create_styles():
    ss = getSampleStyleSheet()

    styles = {
        'CoverTitle': ParagraphStyle(
            'CoverTitle',
            fontName=FONT_BOLD,
            fontSize=24,
            leading=30,
            textColor=PRIMARY_DARK,
            alignment=0,
            spaceAfter=8
        ),
        'CoverSubtitle': ParagraphStyle(
            'CoverSubtitle',
            fontName=FONT_MAIN,
            fontSize=12,
            leading=16,
            textColor=TEXT_DARK,
            alignment=0,
            spaceAfter=15
        ),
        'CoverMeta': ParagraphStyle(
            'CoverMeta',
            fontName=FONT_MAIN,
            fontSize=9,
            leading=13,
            textColor=TEXT_MUTED,
            alignment=0
        ),
        'ChapterTitle': ParagraphStyle(
            'ChapterTitle',
            fontName=FONT_BOLD,
            fontSize=16,
            leading=20,
            textColor=PRIMARY_DARK,
            spaceBefore=12,
            spaceAfter=4,
            keepWithNext=True
        ),
        'ChapterSubtitle': ParagraphStyle(
            'ChapterSubtitle',
            fontName=FONT_MAIN,
            fontSize=10,
            leading=14,
            textColor=TEXT_MUTED,
            spaceAfter=10,
            keepWithNext=True
        ),
        'SectionTitle': ParagraphStyle(
            'SectionTitle',
            fontName=FONT_BOLD,
            fontSize=12,
            leading=16,
            textColor=TEXT_DARK,
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True
        ),
        'SubSectionTitle': ParagraphStyle(
            'SubSectionTitle',
            fontName=FONT_BOLD,
            fontSize=10,
            leading=14,
            textColor=PRIMARY_DARK,
            spaceBefore=8,
            spaceAfter=3,
            keepWithNext=True
        ),
        'Body': ParagraphStyle(
            'Body',
            fontName=FONT_MAIN,
            fontSize=9,
            leading=13,
            textColor=TEXT_DARK,
            spaceAfter=5
        ),
        'BodyBold': ParagraphStyle(
            'BodyBold',
            fontName=FONT_BOLD,
            fontSize=9,
            leading=13,
            textColor=TEXT_DARK,
            spaceAfter=5
        ),
        'Bullet': ParagraphStyle(
            'Bullet',
            fontName=FONT_MAIN,
            fontSize=8.5,
            leading=12,
            textColor=TEXT_DARK,
            leftIndent=14,
            firstLineIndent=-10,
            spaceAfter=3
        ),
        'CalloutTitle': ParagraphStyle(
            'CalloutTitle',
            fontName=FONT_BOLD,
            fontSize=9,
            leading=12,
            textColor=PRIMARY_DARK,
            spaceAfter=2
        ),
        'CalloutBody': ParagraphStyle(
            'CalloutBody',
            fontName=FONT_MAIN,
            fontSize=8.5,
            leading=11.5,
            textColor=TEXT_DARK
        ),
        'TableHeader': ParagraphStyle(
            'TableHeader',
            fontName=FONT_BOLD,
            fontSize=8,
            leading=10,
            textColor=SURFACE_WHITE,
            alignment=0
        ),
        'TableCell': ParagraphStyle(
            'TableCell',
            fontName=FONT_MAIN,
            fontSize=7.5,
            leading=10,
            textColor=TEXT_DARK,
            alignment=0
        ),
        'TableCellBold': ParagraphStyle(
            'TableCellBold',
            fontName=FONT_BOLD,
            fontSize=7.5,
            leading=10,
            textColor=TEXT_DARK,
            alignment=0
        ),
        'TableCellMono': ParagraphStyle(
            'TableCellMono',
            fontName=FONT_MONO,
            fontSize=7,
            leading=9,
            textColor=PRIMARY_DARK,
            alignment=0
        ),
        'Code': ParagraphStyle(
            'Code',
            fontName=FONT_MONO,
            fontSize=7.5,
            leading=10,
            textColor=CODE_TEXT
        ),
        'TocChapter': ParagraphStyle(
            'TocChapter',
            fontName=FONT_BOLD,
            fontSize=9,
            leading=13,
            textColor=PRIMARY_DARK
        ),
        'TocSection': ParagraphStyle(
            'TocSection',
            fontName=FONT_MAIN,
            fontSize=8,
            leading=11,
            textColor=TEXT_DARK,
            leftIndent=12
        )
    }
    return styles

# Global styles instance
STYLES = create_styles()

# -------------------------------------------------------------------------
# FLOWABLE GENERATORS
# -------------------------------------------------------------------------
def p(text: str, style_name: str = 'Body') -> Paragraph:
    """Helper to create a formatted paragraph with XML escaping."""
    safe_text = escape_xml(text)
    return Paragraph(safe_text, STYLES[style_name])

def bullet(text: str) -> Paragraph:
    """Helper to create bullet point."""
    safe_text = f"• {escape_xml(text)}"
    return Paragraph(safe_text, STYLES['Bullet'])

def callout(title: str, text: str, ctype: str = 'info') -> Table:
    """Creates a beautifully styled callout box with accent border."""
    if ctype == 'tip':
        bg_col = GREEN_BG
        border_col = GREEN_ACCENT
        title_prefix = "<b>[PRO-TIP / OPTIMIZATION]</b> "
    elif ctype == 'warning':
        bg_col = AMBER_BG
        border_col = AMBER_ACCENT
        title_prefix = "<b>[IMPORTANT / ATTENTION]</b> "
    elif ctype == 'interview':
        bg_col = LAVENDER_BG
        border_col = PRIMARY
        title_prefix = "<b>[INTERVIEW & VIVA INSIGHT]</b> "
    elif ctype == 'governance':
        bg_col = RED_BG
        border_col = RED_ACCENT
        title_prefix = "<b>[FINTECH GOVERNANCE NOTICE]</b> "
    else: # info
        bg_col = LAVENDER_BG
        border_col = PRIMARY_DARK
        title_prefix = "<b>[CORE FINTECH CONCEPT]</b> "

    content = [
        Paragraph(title_prefix + escape_xml(title), STYLES['CalloutTitle']),
        Spacer(1, 2),
        Paragraph(escape_xml(text), STYLES['CalloutBody'])
    ]

    t = Table([[content]], colWidths=[CONTENT_WIDTH])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_col),
        ('BOX', (0,0), (-1,-1), 1, border_col),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    return t

def code_block(code_content: str, language_label: str = "") -> Table:
    """Creates a styled code snippet box."""
    code_lines = [escape_xml(line) for line in code_content.strip().split('\n')]
    formatted_code = '<br/>'.join(code_lines)
    
    header_text = f"<b>CODE SNIPPET ({language_label})</b>" if language_label else "<b>CODE SNIPPET</b>"
    cell_content = [
        Paragraph(header_text, ParagraphStyle('CodeHdr', fontName=FONT_BOLD, fontSize=7, leading=9, textColor=TEXT_MUTED)),
        Spacer(1, 3),
        Paragraph(formatted_code, STYLES['Code'])
    ]
    t = Table([[cell_content]], colWidths=[CONTENT_WIDTH])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CODE_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_LIGHT),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    return t

def make_table(headers: list, rows: list, col_widths: list, mono_cols: list = None) -> Table:
    """Creates an autowrapping, high-contrast, clean table."""
    mono_cols = mono_cols or []
    table_data = []

    # Headers
    header_row = [Paragraph(escape_xml(str(h)), STYLES['TableHeader']) for h in headers]
    table_data.append(header_row)

    # Data Rows
    for r in rows:
        row_cells = []
        for idx, val in enumerate(r):
            style = STYLES['TableCellMono'] if idx in mono_cols else STYLES['TableCell']
            row_cells.append(Paragraph(escape_xml(str(val)), style))
        table_data.append(row_cells)

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_DARK),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [SURFACE_WHITE, CANVAS_BG])
    ]))
    return t

def hr() -> HRFlowable:
    """Horizontal rule flowable."""
    return HRFlowable(
        width="100%",
        thickness=0.75,
        color=BORDER_LIGHT,
        spaceBefore=8,
        spaceAfter=8
    )
