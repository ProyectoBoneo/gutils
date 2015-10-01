import inspect

from django.db.models import ProtectedError
from django.core.exceptions import ImproperlyConfigured

from django.shortcuts import render_to_response, Http404, HttpResponse, \
    get_object_or_404, RequestContext, redirect
from gutils.generic.json import dict_to_json, json_to_dict
from gutils.django.shortcuts import render_to_json_response
from .base import PermissionsBaseView, DeleteView, View


class FilterMixin:
    form_class = None
    store_form_data = True

    def __init__(self):
        self.model = None
        self._filtro_form = None

    def _get_model(self):
        if self.model is not None:
            return self.model
        else:
            return self.get_base_queryset().model

    def _add_filter_to_queryset(self, field_name, field_value, queryset):
        if self._filtro_form.has_filters:
            lookup = self._filtro_form.Meta.filters.get(field_name, field_name)  # lookup defaults to field name
        else:
            lookup = field_name
        filter_kwargs = {lookup: field_value}
        return queryset.filter(**filter_kwargs)

    def _get_form_fields(self):
        return [f for f in self._filtro_form.fields if f != 'render_pdf_report' and
                f != 'render_xls_report']

    def _get_session_key(self):
        model = self._get_model()
        return '{}-{}-stored-filters'.format(self.__class__.__name__.lower(), model.__name__.lower())

    def _store_form_data(self, request, form):
        """
        Stores filter form data in the session
        :param form:
        :return:
        """
        request.session[self._get_session_key()] = dict_to_json(form.cleaned_data)

    def _restore_form_data(self, request):
        """
        Restores filter form data stored in the session
        :return: restored form_data
        """
        form_data = {}
        json_dump = request.session.get(self._get_session_key(), None)
        if json_dump is not None:
            form_data = json_to_dict(json_dump)
        return form_data

    def _filter_queryset_with_form_data(self, queryset, get_value_from_key):
        """
        Filters the queryset using get_value_from_key function to get the values from the form
        :param queryset: queryset to be filtered
        :param get_value_from_key: function that receives a key and returns a value from the form
        :return: filtered queryset
        """
        elementos_mostrados = None
        for field in self._get_form_fields():
            if field == 'elementos_mostrados':
                elementos_mostrados = get_value_from_key(field)
            else:
                field_value = get_value_from_key(field)
                if field_value:
                    queryset = self._add_filter_to_queryset(field, field_value, queryset)
        if elementos_mostrados:
            queryset = queryset[0:elementos_mostrados]
        return queryset

    def _filter_queryset(self, request):
        """
        Filters the base_queryset using the filter_form's values
        :return: queryset
        """
        queryset = self.get_base_queryset()
        if request.GET:
            self._filtro_form = self.form_class(self.request.GET)
            if self._filtro_form.is_valid():
                if self.store_form_data:
                    self._store_form_data(request, self._filtro_form)
                queryset = self._filter_queryset_with_form_data(queryset,
                                                                lambda fld:
                                                                self._filtro_form.cleaned_data.get(fld, None))
        else:
            form_initial = self._restore_form_data(request) if self.store_form_data else None
            if form_initial:
                try:
                    self._filtro_form = self.form_class(form_initial)
                    if self._filtro_form.is_valid():
                        queryset = self._filter_queryset_with_form_data(queryset,
                                                                        lambda fld:
                                                                        self._filtro_form.cleaned_data.get(fld, None))
                except TypeError:
                    self._filtro_form = self.form_class()
                    queryset = self._filter_queryset_with_form_data(queryset,
                                                                    lambda fld:
                                                                    self._filtro_form.fields[fld].initial)
            else:
                self._filtro_form = self.form_class()
                queryset = self._filter_queryset_with_form_data(queryset,
                                                                lambda fld:
                                                                self._filtro_form.fields[fld].initial)
        return queryset

    def get_base_queryset(self):
        """
        Overridable method used to define the base queryset to be filtered
        :return: queryset
        """
        if self.model is None:
            raise ImproperlyConfigured("'{}' must define 'model' or override get_base_queryset".format(self.__class__))
        return self.model.objects.all()


class ProtectedDeleteView(DeleteView, PermissionsBaseView):

    def delete(self, request, *args, **kwargs):
        relaciones_con_objetos = []
        try:
            http_succes = super(ProtectedDeleteView, self).delete(request, *args, **kwargs)
            return http_succes
        except ProtectedError:
            relaciones = self.object._meta.get_all_related_objects()
            for relacion in relaciones:
                relacion.nombre = relacion.model._meta.verbose_name_plural
                nombre_relacion = relacion.get_accessor_name()
                objeto_relacionado = getattr(self.object, nombre_relacion)
                try:
                    relacion.objetos = list(objeto_relacionado.all())
                    if relacion.objetos:
                        relaciones_con_objetos.append(relacion)
                except TypeError:
                    relacion.objetos = None
            context = {'object': self.object,
                       'relaciones': relaciones_con_objetos,
                       }
            return render_to_response('utils/integridad_referencial.html', context)


class ServiceView(View):
    parameters = {}
    request = None
    method_not_found = Http404('Method not found')
    server_error = HttpResponse('Error while handling the request', status=500)

    def get_method(self, request_option):
        methods = inspect.getmembers(self, inspect.ismethod)
        try:
            method = [m[1] for m in methods if m[0] == request_option and
                      hasattr(m[1], 'servicemethod') and m[1].servicemethod][0]
            return method
        except IndexError:
            return None

    def get(self, request):
        self.request = request
        request_get_copy = self.request.GET.copy()
        request_option = request_get_copy.get('request', None)
        if request_option:
            request_get_copy.pop('request')
            self.parameters = request_get_copy
            method = self.get_method(request_option)
            if method is not None:
                try:
                    context = method()
                except Exception as e:
                    return self.server_error
            else:
                return self.method_not_found
        else:
            return self.method_not_found
        return render_to_json_response(context)


class DynamicFormRenderingView(View):
    form_class = None
    template_name = None

    def __init__(self):
        super(DynamicFormRenderingView, self).__init__()
        if not self.template_name:
            raise ImproperlyConfigured("'{}' must define template_name".format(self.__class__))
        if not self.form_class:
            raise ImproperlyConfigured("'{}' must define form_class".format(self.__class__))

    def get(self, request):
        if request.GET:
            form = self.form_class(request.GET)
            if form.is_valid():
                return HttpResponse("valid")
        else:
            form = self.form_class()
        return render_to_response(self.template_name,
                                  {'form': form})


class ModelActionView(View):
    model = None
    template_name = None
    success_url = None

    def __init__(self, **kwargs):
        super(ModelActionView, self).__init__(**kwargs)
        self.object = None
        self.request = None
        if self.model is None:
            raise ImproperlyConfigured("'{}' must define model".format(self.__class__))
        if self.template_name is None:
            raise ImproperlyConfigured("'{}' must define template_name".format(self.__class__))
        if self.success_url is None:
            raise ImproperlyConfigured("'{}' must define success_url".format(self.__class__))

    def model_action(self, instance):
        pass

    def get(self, request, *args, **kwargs):
        self.request = request
        instance = get_object_or_404(self.model, pk=kwargs.get('pk', None))
        context = {'object': instance}
        return render_to_response(self.template_name, context, context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        self.request = request
        instance = get_object_or_404(self.model, pk=kwargs.get('pk', None))
        self.model_action(instance)
        return redirect(self.success_url)
