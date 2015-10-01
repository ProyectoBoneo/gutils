import xlwt
from xlwt import Style

header_font = xlwt.Font()
header_font.bold = True

header_pattern = xlwt.Pattern()
header_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
header_pattern.pattern_fore_colour = Style.colour_map['light_green']

border_normal = xlwt.Borders()
gray = Style.colour_map['gray80']
border_normal.bottom_colour = gray
border_normal.top_colour = gray
border_normal.left_colour = gray
border_normal.right_colour = gray
border_normal.left = xlwt.Borders.THIN
border_normal.top = xlwt.Borders.THIN
border_normal.bottom = xlwt.Borders.THIN
border_normal.right = xlwt.Borders.THIN

border = xlwt.Borders()
border.bottom_colour = gray
border.top_colour = gray
border.left_colour = gray
border.right_colour = gray
border.left = xlwt.Borders.THIN
border.top = xlwt.Borders.THIN
border.bottom = xlwt.Borders.THIN
border.right = xlwt.Borders.THIN

header_begin_xls = xlwt.XFStyle()
header_begin_xls.font = header_font
header_begin_xls.borders = border
header_begin_xls.pattern = header_pattern

header_middle_xls = xlwt.XFStyle()
header_middle_xls.font = header_font
header_middle_xls.borders = border
header_middle_xls.pattern = header_pattern

header_end_xls = xlwt.XFStyle()
header_end_xls.font = header_font
header_end_xls.borders = border
header_end_xls.pattern = header_pattern

normal_xls = xlwt.XFStyle()
normal_xls.borders = border_normal

date_xls = xlwt.XFStyle()
date_xls.num_format_str = 'dd/mm/yyyy'
date_xls.borders = border_normal


class XlsStyles:
    NORMAL = normal_xls
    DATE = date_xls
    HEADER_BEGIN = header_begin_xls
    HEADER_MIDDLE = header_middle_xls
    HEADER_END = header_end_xls