import re
import datetime

from django.db import models
from django.db.models import FieldDoesNotExist

from django import forms

from gutils.django.forms import BaseForm, BaseModelForm


class BaseFormsetForm(BaseForm):
    DELETE = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(BaseFormsetForm, self).__init__(*args, **kwargs)
        self.fields['DELETE'].widget.attrs['hidden'] = 'hidden'


class BaseLinkedFormsetForm(BaseFormsetForm):
    linked_line_number = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super(BaseLinkedFormsetForm, self).__init__(*args,  **kwargs)
        self.fields['linked_line_number'].widget.attrs['hidden'] = 'hidden'


class BaseFormsetModelForm(BaseModelForm):
    DELETE = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(BaseFormsetModelForm, self).__init__(*args, **kwargs)
        self.fields['DELETE'].widget.attrs['hidden'] = 'hidden'


class BaseLinkedFormsetModelForm(BaseFormsetModelForm):
    linked_line_number = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super(BaseLinkedFormsetModelForm, self).__init__(*args,  **kwargs)
        self.fields['linked_line_number'].widget.attrs['hidden'] = 'hidden'


def get_formset_instance_attributes_from_dict(prefix, data):
    regex = '{}-(?P<number>\d+)-(?P<attribute>\w+)'.format(prefix)
    instance_parameters = {}
    for data_key, data_value in data.items():
        re_match = re.match(regex, data_key)
        if re_match:
            instance_number = re_match.group('number')
            attribute_name = re_match.group('attribute')
            if instance_number:
                if instance_number not in instance_parameters:
                    instance_parameters[instance_number] = {}
                instance_parameters[instance_number][attribute_name] = data_value
    return instance_parameters


def get_formset_instances_from_dict(model, prefix, data, fields=None):
    instance_attributes = get_formset_instance_attributes_from_dict(prefix, data)
    instances = []
    for k, attributes in instance_attributes.items():
        instance_kwargs = {}
        for attribute_name, value in attributes.items():
            try:
                field = model._meta.get_field_by_name(attribute_name)[0]
            except (IndexError, FieldDoesNotExist):
                field = None
            if field:
                if not value:
                    valor = None
                else:
                    if isinstance(field, (models.IntegerField, models.BigIntegerField,
                                          models.AutoField, models.ForeignKey)):
                        valor = int(value)
                    elif isinstance(field, models.FloatField):
                        valor = float(value)
                    elif isinstance(field, models.DateField):
                        valor = datetime.datetime.strptime(value, "%d/%m/%Y").date()
                    elif isinstance(field, models.DateTimeField):
                        valor = datetime.datetime.strptime(value, "%d/%m/%Y %H:%M")
                    else:
                        valor = str(value)
                if fields is None or attribute_name in fields:
                    instance_kwargs[attribute_name] = valor
        instances.append(model(**instance_kwargs))
    return instances