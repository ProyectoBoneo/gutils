from django.utils.safestring import mark_safe

from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured

from gutils.django.forms.typeahead.lookups import REGISTERED_LOOKUPS
from django import forms


class TypeaheadModelWidget(forms.TextInput):

    lookup = None
    form_field_name = None

    def __init__(self, lookup, attrs=None):
        lookup_name = lookup.__name__
        if len([l for l in REGISTERED_LOOKUPS if l.__name__ == lookup_name]) == 0:
            raise ImproperlyConfigured("'{}' is not registered as a lookup. Please use register_lookup".format(
                lookup_name))
        super(TypeaheadModelWidget, self).__init__(attrs)
        self.lookup = lookup
        self.lookup_name = self.lookup.__name__
        self.model_description = self.lookup.get_model_description()

    def get_typeahead_input_id(self, attrs):
        return '{}-{}'.format(attrs.get('id', ''), 'typeahead')

    def render(self, name, value, attrs=None):
        self.form_field_name = name
        if attrs is None:
            attrs = {}
        if self.attrs:
            attrs.update(self.attrs)
        attrs['class'] = attrs.get('class', '') + ' typeahead-form-input form-control '
        attrs['type'] = 'hidden'
        attrs['data-lookup-name'] = self.lookup_name
        attrs['data-lookup-model-description'] = self.model_description
        attrs['data-lookup-url'] = reverse('typeahead')
        attrs['data-add-url'] = reverse('typeahead-add', kwargs={'lookup_name': self.lookup_name})
        attrs['data-lookup-activated'] = 'false'
        attrs['data-initial-description'] = self.lookup.get_object_description(value) if value else ''
        attrs['data-initial-value'] = value
        form_input = super(TypeaheadModelWidget, self).render(name, value, attrs)
        return mark_safe(form_input)


class TypeaheadDropDownModelWidget(TypeaheadModelWidget):

    def _inner_rendering(self, name, value, attrs=None):
        rendering = super(TypeaheadDropDownModelWidget, self).render(name, value, attrs)
        dropdown_button = """
                          <a href='#void' class='btn btn-default' id='{}-dropdown'>
                          <i class="fa fa-chevron-circle-down"></i>
                          </a>
                          """.format(self.get_typeahead_input_id(attrs))
        return mark_safe('\n'.join([rendering, dropdown_button]))

    def render(self, name, value, attrs=None):
        return mark_safe('\n'.join(['<div>', self._inner_rendering(name, value, attrs), '</div>']))


class TypeaheadDropDownAddModelWidget(TypeaheadDropDownModelWidget):

    def _inner_rendering(self, name, value, attrs=None):
        rendering = super(TypeaheadDropDownAddModelWidget, self)._inner_rendering(name,
                                                                                  value, attrs)
        add_button = """
                     <a href='#void' class='btn btn-default' id='{}-dropdown-add'>
                         <i class="fa fa-plus-circle"></i>
                     </a>
                     """.format(self.get_typeahead_input_id(attrs))
        return mark_safe('\n'.join([rendering, add_button]))

    def render(self, name, value, attrs=None):
        return mark_safe('\n'.join(['<div>', self._inner_rendering(name, value, attrs), '</div>']))
