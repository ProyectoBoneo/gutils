import os
import random
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fonts')

pdfmetrics.registerFont(TTFont("Arial", os.path.join(FONTS_DIR, 'arial.ttf')))
pdfmetrics.registerFont(TTFont("Arial-Bold", os.path.join(FONTS_DIR, 'arial-bold.ttf')))
pdfmetrics.registerFont(TTFont("Interleaved2of5", os.path.join(FONTS_DIR, 'Code2Of5Interleaved.ttf')))

_PDF_STYLES = getSampleStyleSheet()


class PdfStyles:
    _ADDED_STYLES = []
    _DEFAULT_FONT_NAME = 'Arial'
    _VERY_LARGE_FONT_SIZE = 24
    _LARGE_FONT_SIZE = 18
    _DEFAULT_FONT_SIZE = 10
    _SMALL_FONT_SIZE = 8
    _VERY_SMALL_FONT_SIZE = 6

    LEFT_ALIGN = TA_LEFT
    CENTER_ALIGN = TA_CENTER
    RIGHT_ALIGN = TA_RIGHT

    NORMAL = ParagraphStyle(name='NormalText', parent=_PDF_STYLES['Normal'],
                            fontName=_DEFAULT_FONT_NAME, fontSize=_DEFAULT_FONT_SIZE)

    LARGE = ParagraphStyle(name='LargeText', parent=NORMAL, fontSize=_LARGE_FONT_SIZE)
    VERY_LARGE = ParagraphStyle(name='VeryLargeText', parent=NORMAL, fontSize=_VERY_LARGE_FONT_SIZE)
    SMALL = ParagraphStyle(name='SmallText', parent=NORMAL, fontSize=_SMALL_FONT_SIZE)
    VERY_SMALL = ParagraphStyle(name='VerySmallText', parent=NORMAL, fontSize=_VERY_SMALL_FONT_SIZE)

    @classmethod
    def get_style(cls, base_style=NORMAL, alignment=LEFT_ALIGN, bold=False, font_size=None, font_name=None):
        while True:
            style_name = str(random.randint(1, 10**10))
            if style_name not in cls._ADDED_STYLES:
                cls._ADDED_STYLES.append(style_name)
                break
        kwargs = {
            'name': style_name,
            'parent': base_style,
            'alignment': alignment,
        }
        if bold:
            font_search_name = '{}-Bold'.format(base_style.fontName)
            if font_search_name in pdfmetrics.getRegisteredFontNames():
                kwargs['fontName'] = font_search_name
        elif font_name:
            kwargs['fontName'] = font_name

        if font_size:
            kwargs['fontSize'] = font_size

        return ParagraphStyle(**kwargs)