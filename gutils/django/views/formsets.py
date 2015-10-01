import re

from django.core.exceptions import ImproperlyConfigured
from django.db.models import ProtectedError

from django.shortcuts import redirect, render_to_response, RequestContext
from .generic import FilterMixin
from .base import View, CreateView, UpdateView


class ModelFormsetView(View):
    """
    Used for fast data input. Can filter the base queryset
    """
    template_name = None
    formset = None
    formset_prefix = 'form'
    success_url = None
    model = None
    request = None

    def get_queryset(self, *args, **kwargs):
        if self.model is None:
            raise ImproperlyConfigured("'{}' must define 'model' or override 'get_queryset'".
                                       format(self.__class__.__name__))
        else:
            return self.model.objects.all()

    def get_formset(self):
        if self.request.method == 'GET':
            return self.formset(queryset=self.get_queryset(), prefix=self.formset_prefix)
        else:
            return self.formset(self.request.POST)

    def get_context_data(self, *args, **kwargs):
        context = {'formset': self.get_formset(), }
        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()
        return render_to_response(self.template_name, context,
                                  context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()
        formset = context['formset']
        valid = True
        if formset.is_valid():
            forms_to_delete = [form for form in formset.initial_forms if form in formset.deleted_forms]
            for form in forms_to_delete:
                try:
                    form.instance.delete()
                except ProtectedError:
                    form.add_error(None, 'El elemento no puede ser eliminado porque '
                                         'participa en relaciones con otros elementos')
                    valid = False
            if valid:
                formset.save()
        else:
            valid = False
        if valid:
            return redirect(self.success_url)
        else:
            return render_to_response(self.template_name, context, context_instance=RequestContext(request))


class ModelFormsetFilteredView(ModelFormsetView, FilterMixin):
    store_form_data = False

    def get_queryset(self, *args, **kwargs):
        return self._filter_queryset(self.request)

    def get_context_data(self):
        context = super(ModelFormsetFilteredView, self).get_context_data()
        if self.request.method == 'GET':
            context['filter_form'] = self._filtro_form
        return context


class InlineFormsetCreateView(CreateView):
    object = None
    formsets = {}

    def get_formsets(self):
        formsets = {}
        if self.request.method == 'POST':
            for key in self.formsets:
                formsets[key] = self.formsets[key](self.request.POST)
        else:
            for key in self.formsets:
                formsets[key] = self.formsets[key]()
        return formsets

    def get_context_data(self, **kwargs):
        context = super(InlineFormsetCreateView, self).get_context_data(**kwargs)
        context.update(self.get_formsets())
        return context

    def save_formset_instance(self, master_form, form,  instance):
        pass

    def save_formset(self, master_form, formset, key):
        formset.instance = self.object
        for form in formset:
            self.save_formset_instance(master_form, form, form.instance)
        formset.save()

    def form_valid(self, form):
        formsets = self.get_formsets()
        valid = True
        for key in self.formsets:
            if not formsets[key].is_valid():
                valid = False
        if valid:
            self.object = form.save()
            for key in self.formsets:
                self.save_formset(form, formsets[key], key)
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class InlineFormsetUpdateView(UpdateView):
    formsets = {}
    object = None

    def get_formsets(self):
        formsets = {}
        if self.request.method == 'POST':
            for key in self.formsets:
                formsets[key] = self.formsets[key](self.request.POST, instance=self.get_object())
        else:
            for key in self.formsets:
                formsets[key] = self.formsets[key](instance=self.get_object())
        return formsets

    def get_context_data(self, **kwargs):
        context = super(InlineFormsetUpdateView, self).get_context_data(**kwargs)
        context.update(self.get_formsets())
        return context

    def save_formset_instance(self, master_form, form,  instance):
        pass

    def save_formset(self, master_form, formset, key):
        formset.instance = self.object
        for form in formset:
            if not (form in formset.extra_forms and not form.has_changed()):
                self.save_formset_instance(master_form, form, form.instance)
        formset.save()

    def form_valid(self, form):
        formsets = self.get_formsets()
        valid = True
        for key in self.formsets:
            if not formsets[key].is_valid():
                valid = False
        if valid:
            self.object = form.save()
            for key in self.formsets:
                self.save_formset(form, formsets[key], key)
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class InlineLinkedFormsetCreateView(InlineFormsetCreateView):
    """
    InlineLinkedFormset views are used to manipulate models linked to details, which can
    be created, updated and deleted in the same form and are generally hidden
    The difference with normal formset views is that the formsets attribute is defined as follows:
    formsets = {'normal_formset': NormalFormset,
                'linked_detail_formset': {'master': detailformset,
                                          'linked': {'detail_formset_1': (linkedformset, attrname),
                                                     'detail_formset_2': (linkedformset2, attrname2),
                                                     }, },
                }
    attrname: attribute that links the master to the linked model
    """

    def get_subformsets(self):
        subformsets = {}
        for key in self.formsets:
            if isinstance(self.formsets[key], dict):
                formsets = self.formsets[key]['linked']
                for subformset_key in formsets:
                    formset = formsets[subformset_key][0]
                    if self.request.method == 'POST':
                        subformsets[subformset_key] = formset(self.request.POST, prefix=subformset_key)
                    else:
                        subformsets[subformset_key] = formset(queryset=formset.model.objects.none(),
                                                              prefix=subformset_key)
        return subformsets

    def get_formsets(self):
        formsets = {}
        for key in self.formsets:
            if isinstance(self.formsets[key], dict):
                formset = self.formsets[key]['master']
            else:
                formset = self.formsets[key]
            if self.request.method == 'POST':
                formsets[key] = formset(self.request.POST)
            else:
                formsets[key] = formset()
        return formsets

    def get_context_data(self, **kwargs):
        context = super(InlineLinkedFormsetCreateView, self).get_context_data(**kwargs)
        context.update(self.get_subformsets())
        return context

    def save_subformset_instance(self, instance, key):
        instance.save()

    def save_formset(self, master_form, formset, key):
        formset.instance = self.object
        subformset_values = self.get_subformsets()
        if isinstance(self.formsets[key], dict):
            subformsets = self.formsets[key]['linked']
            for subformset_key in subformsets:
                attribute_name = subformsets[subformset_key][1]
                subformset = subformset_values[subformset_key]
                if subformset.is_valid():
                    for form in subformset:
                        must_delete = form.cleaned_data.get('DELETE', False)
                        if not must_delete and not (form in subformset.extra_forms and not form.has_changed()):
                            instance = form.save(commit=False)
                            self.save_subformset_instance(instance, subformset_key)
                            line_number = form.cleaned_data['linked_line_number']
                            for detailform in formset:
                                try:
                                    numero = re.findall('\d+', detailform.prefix)[-1]
                                    if line_number == int(numero):
                                        setattr(detailform.instance, attribute_name, instance)
                                except IndexError:
                                    pass
        formset.save()


class InlineLinkedFormsetUpdateView(InlineFormsetUpdateView):
    """
    InlineLinkedFormset views are used to manipulate models linked to details, which can
    be created, updated and deleted in the same form and are generally hidden
    The difference with normal formset views is that the formsets attribute is defined as follows:
    formsets = {'normal_formset': NormalFormset,
                'linked_detail_formset': {'master': detailformset,
                                          'linked': {'detail_formset_1': (linkedformset, attrname),
                                                     'detail_formset_2': (linkedformset2, attrname2),
                                                     }, },
                }
    attrname: attribute that links the master to the linked model
    """

    def get_subformsets(self):
        subformsets = {}
        for key in self.formsets:
            formset_conf = self.formsets[key]
            if isinstance(formset_conf, dict):
                subformsets_conf = formset_conf['linked']
                for subformset_key in subformsets_conf:
                    formset = subformsets_conf[subformset_key][0]
                    attribute_name = subformsets_conf[subformset_key][1]
                    if self.request.method == 'POST':
                        subformsets[subformset_key] = formset(self.request.POST, prefix=subformset_key)
                    else:
                        instances = [form.instance for form in self.get_formsets()[key]]
                        linked_ids = [getattr(instance, attribute_name).id
                                      for instance in instances
                                      if hasattr(instance, attribute_name) and getattr(instance, attribute_name)]
                        subformsets[subformset_key] = formset(queryset=formset.model.objects.filter(id__in=linked_ids),
                                                              prefix=subformset_key)
        return subformsets

    def get_formsets(self):
        formsets = {}
        for key in self.formsets:
            if isinstance(self.formsets[key], dict):
                formset = self.formsets[key]['master']
            else:
                formset = self.formsets[key]
            if self.request.method == 'POST':
                formsets[key] = formset(self.request.POST, instance=self.get_object())
            else:
                formsets[key] = formset(instance=self.get_object())
        return formsets

    def get_context_data(self, **kwargs):
        context = super(InlineLinkedFormsetUpdateView, self).get_context_data(**kwargs)
        context.update(self.get_subformsets())
        if not self.request.method == 'POST':
            for key in self.get_formsets():
                formset = context[key]
                if isinstance(self.formsets[key], dict):
                    subformsets = self.formsets[key]['linked']
                    for subformset_key in subformsets:
                        attribute_name = subformsets[subformset_key][1]
                        subformset = context[subformset_key]
                        for subform in subformset:
                            for form in formset:
                                if getattr(form.instance, attribute_name) == subform.instance:
                                    line_number = re.findall('\d+', form.prefix)[-1]
                                    if line_number:
                                        subform.fields['linked_line_number'].initial = line_number
        return context

    def save_subformset_instance(self, instance, key):
        instance.save()

    def save_formset(self, master_form, formset, key):
        formset.instance = self.object
        subformset_values = self.get_subformsets()
        instances_to_delete = []
        if isinstance(self.formsets[key], dict):
            subformsets = self.formsets[key]['linked']
            for subformset_key in subformsets:
                attribute_name = subformsets[subformset_key][1]
                subformset = subformset_values[subformset_key]
                if subformset.is_valid():
                    for form in subformset:
                        must_delete = form.cleaned_data.get('DELETE', False)
                        if must_delete and form.instance.id is None:
                            instances_to_delete.append(form.instance)
                        elif not (form in subformset.extra_forms and not form.has_changed()) and not must_delete:
                            instance = form.save(commit=False)
                            self.save_subformset_instance(instance, subformset_key)
                            line_number = form.cleaned_data['linked_line_number']
                            for detailform in formset:
                                try:
                                    numero = re.findall('\d+', detailform.prefix)[-1]
                                    if line_number == int(numero):
                                        setattr(detailform.instance, attribute_name, instance)
                                except IndexError:
                                    pass
        formset.save()
        for instance in instances_to_delete:
            instance.delete()
