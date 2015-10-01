from django.db import models
from gutils.django import forms


class CUITField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 11
        super(CUITField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(CUITField, self).deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.CUITField,
        }
        defaults.update(kwargs)
        return super(CUITField, self).formfield(**defaults)


class DNIField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 8
        super(DNIField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(DNIField, self).deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.DNIField,
        }
        defaults.update(kwargs)
        return super(DNIField, self).formfield(**defaults)