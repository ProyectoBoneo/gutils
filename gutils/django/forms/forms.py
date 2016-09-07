from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist

from django import forms

from gutils.django.forms import DatetimeInput


def add_class_to_widget(widget, *css_classes):
    """
    Adds a css class to a given widget
    """
    css_string = " ".join(css_classes)
    if 'class' in widget.attrs:
        widget.attrs['class'] += ' {} '.format(css_string)
    else:
        widget.attrs['class'] = css_string


def set_field_attributes(fields, errors):
    """
    Sets the type and css class of basic form fields
    """
    for field in fields:
        field_instance = fields[field]
        widget = field_instance.widget
        if isinstance(field_instance, forms.DateField) and isinstance(widget, forms.TextInput):
            field_instance.format = '%d/%m/%Y'
            add_class_to_widget(widget, 'date')
            widget.attrs['type'] = 'text'
        elif isinstance(field_instance, forms.DateTimeField):
            field_instance.format = '%d/%m/%Y %H:%M'
            if isinstance(widget, forms.TextInput):
                add_class_to_widget(widget, 'datetime')
            elif isinstance(widget, DatetimeInput):
                add_class_to_widget(widget.widgets[0], 'date')
        elif isinstance(field_instance, forms.FloatField) and isinstance(widget, forms.TextInput):
            add_class_to_widget(widget, 'float')
        elif isinstance(field_instance, forms.IntegerField) and isinstance(widget, forms.TextInput):
            add_class_to_widget(widget, 'int')
        elif isinstance(field_instance, forms.CharField) and isinstance(widget, forms.TextInput):
            add_class_to_widget(widget, 'char')

        if isinstance(widget, forms.CheckboxSelectMultiple):
            add_class_to_widget(widget, 'checkbox-multiple-select')

        if field in errors:
            add_class_to_widget(widget, 'with_errors')
            if 'title' not in widget.attrs:
                widget.attrs['title'] = '; '.join(errors[field])

        add_class_to_widget(widget, 'form-control')


class GFormMixin:
    fields = {}
    excluded_fields = ('creation_date', 'update_date', 'user_created', 'user_updated', 'empresa')

    def model_fields(self):
        fields = [field for field in self.fields if field not in self.excluded_fields]
        return fields

    def render_layout(self):
        form_layout = '<div class="formfields">'
        for field_name in self.model_fields():
            field = self[field_name]
            form_layout += \
                """
                <div id="{0}" class="form-group">
                    {1}
                    {2}
                    {3}
                    <span class="helptext">{4}</span>
                </div>
                """.format(field_name, str(field.label_tag()), str(field),
                           str(field.errors), str(field.help_text))
        form_layout += '</div>'
        return mark_safe(form_layout)


class BaseModelForm(forms.ModelForm, GFormMixin):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(BaseModelForm, self).__init__(*args, **kwargs)
        set_field_attributes(self.fields, self.errors)


class BaseForm(forms.Form, GFormMixin):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(BaseForm, self).__init__(*args, **kwargs)
        set_field_attributes(self.fields, self.errors)


class BaseFilterForm(BaseForm):

    @property
    def filter_button(self):
        try:
            button = render_to_string('gutils/forms/filter_form_button.html')
        except TemplateDoesNotExist:
            button = """
                        <button class="btn btn-default" type="submit">
                            <i class="fa fa-filter"></i> Filtrar
                        </button>
                     """
        return mark_safe(button)

    def has_filters(self):
        try:
            self.Meta.filters
        except AttributeError:
            return False
        else:
            return True


class BaseFilterReportForm(BaseFilterForm):
    render_pdf_report = forms.BooleanField(required=False, initial=False)
    render_xls_report = forms.BooleanField(required=False, initial=False)

    @property
    def filter_buttons(self):
        try:
            submit_buttons = render_to_string('gutils/forms/filter_report_form_buttons.html')
        except TemplateDoesNotExist:
            submit_buttons = """
                                <button class="button" type="submit" onclick="filterController.filter_click(this)">
                                    <i class="fa fa-filter"></i> Filtrar
                                </button>

                                <button class="button" type="submit" onclick="filterController.filter_print(this)">
                                    <i class="fa fa-print"></i> Imprimir
                                </button>

                                <button class="button" type="submit" onclick="filterController.filter_sheet(this)">
                                    <i class="fa fa-file-excel-o"></i> Planilla
                                </button>
                            """
        return mark_safe("""<div class="filter-buttons inline">""" + str(self['render_pdf_report']) +
                         str(self['render_xls_report']) +
                         submit_buttons + self.render_elementos_mostrados() + """</div>""")

    def __init__(self, *args, **kwargs):
        super(BaseFilterReportForm, self).__init__(*args, **kwargs)
        self.fields['render_pdf_report'].widget.attrs['hidden'] = 'hidden'
        self.fields['render_pdf_report'].widget.attrs['class'] = ''
        self.fields['render_xls_report'].widget.attrs['hidden'] = 'hidden'
        self.fields['render_xls_report'].widget.attrs['class'] = ''
