from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType

from django.views import generic
from django.views.decorators.cache import never_cache
from django.shortcuts import render_to_response, RequestContext


class PermissionsBaseView:
    ignore_permissions = False

    def __init__(self):
        self.queryset = None
        self.model = None
        self.BASE_PERMISSION = ''

    def _validate_definition(self):
        if self.queryset is not None:
            raise ImproperlyConfigured("'{}' (Permissions view) must define 'model' and not 'queryset' due to manager" +
                                       " customization. Override get_queryset (or get_base_queryset for " +
                                       "FilteredViews) if you need a custom queryset".format(self.__class__.__name__))
        if self.model is None:
            raise ImproperlyConfigured("'{}' (Kiwi view) must define 'model'".format(self.__class__.__name__))

    def get_queryset(self):
        pass

    def get_object(self):
        pass

    def get_content_type(self):
        if self.model is not None:
            content_type = ContentType.objects.get_for_model(self.model)
        else:
            try:
                model = self.get_queryset().model
                content_type = ContentType.objects.get_for_model(model)
            except AttributeError:
                try:
                    model = self.get_object()
                    content_type = ContentType.objects.get_for_model(model)
                except AttributeError:
                    content_type = None
        return content_type

    def check_permission(self, request):
        if self.ignore_permissions:
            return True
        else:
            content_type = self.get_content_type()
            content_type_model = content_type.model
            content_type_app = content_type.app_label
            permission_codename = '{}.{}_{}'.format(content_type_app, self.BASE_PERMISSION, content_type_model)
            return request.user.has_perm(permission_codename)

    def check_additional_conditions(self, request, *args, **kwargs):
        """
        Checks additional conditions regarding authorization
        :return: bool: True - has permission, False - doesn't have permission
        """
        return True

    @classmethod
    def additional_conditions_denied_response(cls, request, *args, **kwargs):
        """
        Optional. Used to render a different response due to additional conditions
        :return: HttpResponse
        """
        return None

    @classmethod
    def permission_denied_response(cls, request):
        """
        Used to render a response showing unauthorized status
        :return: HttpResponse
        """
        return render_to_response('permissions/permission_denied.html', {},
                                  context_instance=RequestContext(request))


class View(generic.View):

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        return super(View, self).dispatch(request, *args, **kwargs)


class ListView(generic.ListView, PermissionsBaseView):

    BASE_PERMISSION = 'list'

    def __init__(self, **kwargs):
        self._validate_definition()
        super(ListView, self).__init__(**kwargs)

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        if self.check_permission(request):
            if self.check_additional_conditions(request, *args, **kwargs):
                return super(ListView, self).dispatch(request, *args, **kwargs)
            else:
                return self.additional_conditions_denied_response(request, *args, **kwargs)
        else:
            return self.permission_denied_response(request)


class CreateView(generic.CreateView, PermissionsBaseView):

    BASE_PERMISSION = 'add'

    def __init__(self, **kwargs):
        self._validate_definition()
        super(CreateView, self).__init__(**kwargs)

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        if self.check_permission(request):
            if self.check_additional_conditions(request, *args, **kwargs):
                return super(CreateView, self).dispatch(request, *args, **kwargs)
            else:
                return self.additional_conditions_denied_response(request, *args, **kwargs)
        else:
            return self.permission_denied_response(request)


class UpdateView(generic.UpdateView, PermissionsBaseView):

    BASE_PERMISSION = 'change'

    def __init__(self, **kwargs):
        self._validate_definition()
        super(UpdateView, self).__init__(**kwargs)

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        if self.check_permission(request):
            if self.check_additional_conditions(request, *args, **kwargs):
                return super(UpdateView, self).dispatch(request, *args, **kwargs)
            else:
                return self.additional_conditions_denied_response(request, *args, **kwargs)
        else:
            return self.permission_denied_response(request)


class FormView(generic.FormView):

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        return super(FormView, self).dispatch(request, *args, **kwargs)


class DetailView(generic.DetailView, PermissionsBaseView):

    BASE_PERMISSION = 'view'

    def __init__(self, **kwargs):
        self._validate_definition()
        super(DetailView, self).__init__(**kwargs)

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        if self.check_permission(request):
            if self.check_additional_conditions(request, *args, **kwargs):
                return super(DetailView, self).dispatch(request, *args, **kwargs)
            else:
                return self.additional_conditions_denied_response(request, *args, **kwargs)
        else:
            return self.permission_denied_response(request)


class DeleteView(generic.DeleteView, PermissionsBaseView):

    BASE_PERMISSION = 'delete'

    def __init__(self, **kwargs):
        self._validate_definition()
        super(DeleteView, self).__init__(**kwargs)

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        if self.check_permission(request):
            if self.check_additional_conditions(request, *args, **kwargs):
                return super(DeleteView, self).dispatch(request, *args, **kwargs)
            else:
                return self.additional_conditions_denied_response(request, *args, **kwargs)
        else:
            return self.permission_denied_response(request)


class TemplateView(generic.TemplateView, PermissionsBaseView):

    BASE_PERMISSION = None
    ignore_permissions = True

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        if self.check_permission(request):
            if self.check_additional_conditions(request, *args, **kwargs):
                return super(TemplateView, self).dispatch(request, *args, **kwargs)
            else:
                return self.additional_conditions_denied_response(request, *args, **kwargs)
        else:
            return self.permission_denied_response(request)