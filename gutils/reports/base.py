import xlwt
from reportlab.platypus import BaseDocTemplate, PageTemplate
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from django.shortcuts import HttpResponse


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 8)
        self.drawRightString(self._pagesize[0] - 18*mm, self._pagesize[1] - 10*mm,
                             "Página {} de {}".format(self._pageNumber, page_count))


class BaseReport:

    def get_document_title(self):
        return self.get_file_name()

    def get_file_name(self):
        return 'report'

    def get_xls_file_name(self, filename):
        return '{}.xls'.format(filename.strip())

    def get_pdf_file_name(self, filename):
        return '{}.pdf'.format(filename.strip())

    def fill_xls_document(self, document, context):
        pass

    def fill_pdf_document(self, document, context):
        pass

    def get_margins(self):
        return {'top': 10*mm,
                'right': 10*mm,
                'bottom': 10*mm,
                'left': 10*mm,
                }

    def get_page_size(self):
        return portrait(A4)

    def render_xls_report(self, context, file_name=None):
        self.context = context
        response = HttpResponse(content_type='application/vnd.ms-excel')
        if not file_name:
            file_name = self.get_file_name()
        file_name = self.get_xls_file_name(file_name)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)
        document = xlwt.Workbook()
        self.fill_xls_document(document, context)
        document.save(response)
        return response

    def get_create_document_kwargs(self):
        margins = self.get_margins()
        kwargs = {'pagesize': self.get_page_size(),
                  'rightMargin': margins['right'],
                  'leftMargin': margins['left'],
                  'topMargin': margins['top'],
                  'bottomMargin': margins['bottom'],
                  }
        page_templates = self.get_page_templates()
        if page_templates:
            kwargs['pageTemplates'] = page_templates
        return kwargs

    def get_frames(self):
        return []

    def page_drawer(self, canvas, doc):
        return None

    def get_page_templates(self):
        kwargs = {'onPage': self.page_drawer}
        frames = self.get_frames()
        if frames:
            kwargs['frames'] = frames
        return PageTemplate(**kwargs)

    def create_document(self, response):
        return BaseDocTemplate(response, **self.get_create_document_kwargs())

    def render_pdf_report(self, context, file_name=None):
        self.context = context
        response = HttpResponse(content_type='application/pdf')
        if not file_name:
            file_name = self.get_file_name()
        file_name = self.get_pdf_file_name(file_name)
        response['Content-Disposition'] = 'filename="{}"'.format(file_name)

        document = self.create_document(response)
        document.title = self.get_document_title()
        self.fill_pdf_document(document, context)
        return response
