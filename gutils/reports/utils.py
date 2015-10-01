from reportlab.platypus import Paragraph

from .pdf_styles import PdfStyles


class I2Of5Barcode(Paragraph):

    I2OF5_STYLE = PdfStyles.get_style(base_style=PdfStyles.VERY_LARGE,
                                      alignment=PdfStyles.CENTER_ALIGN,
                                      font_name='Interleaved2of5')

    START_CHAR = chr(201)
    STOP_CHAR = chr(202)

    def __init__(self, number):
        number_string = str(number)
        if len(number_string) % 2:
            raise ValueError('"number" must have an even length')
        pairs = map(int, [''.join(t) for t in zip(number_string[0::2], number_string[1::2])])

        encoded_number = self.START_CHAR

        for pair in pairs:
            ordinal = pair + 33 if pair < 95 else pair + 101
            encoded_number += chr(ordinal)

        encoded_number += self.STOP_CHAR
        super(I2Of5Barcode, self).__init__(encoded_number, style=self.I2OF5_STYLE)




