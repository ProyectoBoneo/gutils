import datetime
from reportlab.platypus import Table, Spacer, PageBreak, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.colors import black
from reportlab.lib.units import mm
from reportlab.platypus.doctemplate import SimpleDocTemplate

from django.db import models

from gutils.generic.list import split_list
from gutils.django.models import get_model_field_repr, get_field
from .base import BaseReport, NumberedCanvas
from .pdf_styles import PdfStyles
from .xls_styles import XlsStyles


class BaseModelReport(BaseReport):
    LANDSCAPE = landscape
    PORTRAIT = portrait

    filename = None
    title = None
    model = None
    fields = []
    headers = {}
    ordering = []
    orientation = PORTRAIT
    widths = {}
    models_per_page = 20 if LANDSCAPE else 25

    _fields = None
    _model = None
    _page_header_story = None
    _title = None

    def create_document(self, response):
        return SimpleDocTemplate(response, **self.get_create_document_kwargs())

    def get_page_templates(self):
        return None

    def get_base_queryset(self):
        return self.model.objects.all()

    def get_queryset(self, context):
        if 'queryset' in context:
            queryset = context['queryset']
        else:
            queryset = self.get_base_queryset()

        if 'ordering' in context:
            ordering = context['ordering']
            queryset = queryset.order_by(*ordering)
        elif self.ordering:
            queryset = queryset.order_by(*self.ordering)
        return queryset

    def get_file_name(self):
        return self.filename if self.filename else self.get_page_title()

    def get_page_size(self):
        return portrait(A4) if self.orientation == self.PORTRAIT else landscape(A4)

    def get_widths(self):
        page_width = self.get_page_size()[0] - 20*mm
        percentage_used = sum([value for key, value in self.widths.items()])
        if percentage_used > 100:
            raise ValueError("The total width defined by '{}' adds up to more than 100 percent".format(self.__name__))
        remaining_page_width = 100 - percentage_used
        widths = []
        fields = self.get_field_configuration()
        non_defined_fields = len(fields) - len(self.widths)
        percentage_per_non_defined = round(remaining_page_width/non_defined_fields, 2)
        for field in fields:
            field_name = field['name']
            if field_name in self.widths:
                width = self.widths[field_name]*page_width/100
            else:
                width = percentage_per_non_defined*page_width/100
            widths.append(width)
        return widths

    def get_fields(self):
        if self._fields is None:
            model_fields = self.get_model()._meta.fields
            self._fields = self.fields if self.fields else [field.name for field in model_fields]
        return self._fields

    def get_model(self):
        if self._model is None:
            self._model = self.model if self.model else self.get_base_queryset().model
        return self._model

    def get_field_configuration(self):
        field_configuration = []
        for field in self.get_fields():
            field_element = None
            field_name = field

            if field_name in [f.name for f in self.get_model()._meta.fields]:
                field_element = self.get_model()._meta.get_field_by_name(field_name)[0]

            field_header = self.headers.get(field, None)
            if not field_header:
                if field_element:
                    field_header = field_element.verbose_name.capitalize()
                else:
                    field_header = field_name.capitalize()
            field_configuration.append({'name': field_name, 'header': field_header,
                                        'element': field_element, })

        return field_configuration

    def get_page_title(self):
        if self._title is None:
            self._title = self.title if self.title else self.get_model()._meta.verbose_name.capitalize()
        return self._title

    def get_page_header_story(self):
        if self._page_header_story is None:
            page_header_story = []
            for field_conf in self.get_field_configuration():
                field_header = field_conf['header']
                field_element = field_conf['element']
                if isinstance(field_element, (models.IntegerField, models.AutoField,
                                              models.FloatField, models.BigIntegerField)):
                    header_style = PdfStyles.get_style(PdfStyles.SMALL, alignment=PdfStyles.RIGHT_ALIGN, bold=True)
                else:
                    header_style = PdfStyles.get_style(PdfStyles.SMALL, bold=True)
                page_header_story.append(Paragraph(field_header, style=header_style))
            self._page_header_story = page_header_story
        return self._page_header_story

    def fill_xls_document(self, document, context):
        object_list = self.get_queryset(context)
        sheet = document.add_sheet(self.get_page_title())
        config = self.get_field_configuration()
        for idx, field_conf in enumerate(config):
            field_header = field_conf['header']
            if idx == 0:
                style = XlsStyles.HEADER_BEGIN
            elif id == len(config) - 1:
                style = XlsStyles.HEADER_END
            else:
                style = XlsStyles.HEADER_MIDDLE
            sheet.write(0, idx, field_header, style)
        for idx, instance in enumerate(object_list):
            for jdx, field in enumerate(self.get_fields()):
                    value = get_field(instance, field)
                    if not isinstance(value, (int, float, str, datetime.date)):
                        value = get_model_field_repr(instance, field)
                    style = XlsStyles.NORMAL
                    if isinstance(value, datetime.date):
                        style = XlsStyles.DATE
                    sheet.write(idx + 1, jdx, value, style)

    def fill_pdf_document(self, document, context):
        story = []
        object_list = self.get_queryset(context)
        self.fill_story(object_list, story)
        document.build(story, canvasmaker=NumberedCanvas)

    def fill_story(self,  object_list, story):
        pages = split_list(object_list, self.models_per_page)
        page_count = 0

        for pagina in pages:
            page_count += 1
            values_list = []
            styles_list = []
            for obj in pagina:
                field_value_list = []
                for idx, field in enumerate(self.get_fields()):
                    field_value = get_field(obj, field)
                    value = get_model_field_repr(obj, field)
                    style = PdfStyles.SMALL
                    if isinstance(field_value, (float, int)):
                        styles_list.append(('ALIGN', (idx, 0), (idx, -1), 'RIGHT'))
                        style = PdfStyles.get_style(PdfStyles.SMALL, alignment=PdfStyles.RIGHT_ALIGN)
                    field_value_list.append(Paragraph(value, style=style))
                values_list.append(field_value_list)

            story.append(Paragraph(text=self.get_page_title(), style=PdfStyles.get_style(PdfStyles.LARGE, bold=True)))
            story.append(Spacer(width=10*mm, height=7*mm))
            data = [self.get_page_header_story(), ]
            data.extend(values_list)
            if self.widths:
                table = Table(data, colWidths=self.get_widths())
            else:
                table = Table(data)
            styles_list.extend([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('GRID', (0, 0), (len(self.get_fields()) - 1, 0), 1, black),
                                ])
            table.setStyle(TableStyle(styles_list))
            story.append(table)
            if page_count < len(pages):
                story.append(PageBreak())


