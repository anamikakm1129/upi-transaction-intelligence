"""
Script to generate:
1. docs/UPI_Transaction_Intelligence_Technical_Guide_Hinglish.md
2. docs/UPI_Transaction_Intelligence_Technical_Guide_Hinglish.pdf
3. docs/architecture_diagram.png (already created)
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Segoe UI and Consolas fonts if available
FONTS_AVAILABLE = False
try:
    if os.path.exists('C:/Windows/Fonts/segoeui.ttf'):
        pdfmetrics.registerFont(TTFont('SegoeUI', 'C:/Windows/Fonts/segoeui.ttf'))
        pdfmetrics.registerFont(TTFont('SegoeUI-Bold', 'C:/Windows/Fonts/segoeuib.ttf'))
        pdfmetrics.registerFont(TTFont('SegoeUI-Italic', 'C:/Windows/Fonts/segoeuii.ttf'))
        pdfmetrics.registerFont(TTFont('Consolas', 'C:/Windows/Fonts/consola.ttf'))
        FONTS_AVAILABLE = True
        print("Registered Segoe UI & Consolas fonts.")
except Exception as e:
    print(f"Font registration warning: {e}")

FONT_MAIN = 'SegoeUI' if FONTS_AVAILABLE else 'Helvetica'
FONT_BOLD = 'SegoeUI-Bold' if FONTS_AVAILABLE else 'Helvetica-Bold'
FONT_ITALIC = 'SegoeUI-Italic' if FONTS_AVAILABLE else 'Helvetica-Oblique'
FONT_MONO = 'Consolas' if FONTS_AVAILABLE else 'Courier'

# Custom Canvas for Two-Pass Page Numbering (Page X of Y)
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        # Do not draw headers or footers on the cover page (Page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont(FONT_MAIN, 8)
        self.setFillColor(colors.HexColor("#77736F"))

        # Running Header
        self.drawString(54, 750, "UPI Transaction Intelligence System — Complete Hinglish Technical Guide")
        self.setStrokeColor(colors.HexColor("#ECE8E5"))
        self.setLineWidth(0.75)
        self.line(54, 742, 558, 742)

        # Running Footer
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Confidential & Academic Reference • PhonePe/Razorpay/Fintech Standard")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()

print("NumberedCanvas initialized successfully.")
