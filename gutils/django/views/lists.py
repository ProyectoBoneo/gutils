from django.core.exceptions import ImproperlyConfigured

from gutils.django.views.base import ListView, View

from .generic import FilterMixin


class FilteredListView(ListView, FilterMixin):
    """
    This class is used to extend listviews adding a filter_form to the template
    Needed attributes:
    - form_class: the form defined to filter the view
    - model: the model that is displayed

    Note:
    In the Meta class of the form, a dict called filters can be defined to specify the behavior.
    The key is the name of the field, while the value is the kwarg used in the queryset.
    If the field is not present in this dictionary, the lookup defaults to 'form_field_name=value'
    Example:

    class FilterForm(forms.BaseForm):
        date_from = forms.DateField()
        date_to = forms.DateField()
        value = forms.FloatField()
        price = forms.FloatField()

        class Meta:
            filters = {
                'date_from': 'date__gte',
                'date_to': 'date__lte',
                'value': 'model_value',
            }

    This generates the queryset: model.objects.filter(date__gte=date_from).filter(dete__lte=date_to).
                                      filter(model_value=value).filter(price=price)
    """
    def get_context_data(self, **kwargs):
        context = super(FilteredListView, self).get_context_data(**kwargs)
        context['filter_form'] = self._filtro_form
        return context

    def get_queryset(self):
        return self._filter_queryset(self.request)


class ReportView(View):
    report = None

    def get(self, request, *args, **kwargs):
        context = dict(request.GET.lists())
        context.update(kwargs)
        return self.report().render_pdf_report(context)


class FilteredReportListView(FilteredListView):
    report = None

    def __init__(self, **kwargs):
        super(FilteredReportListView, self).__init__(**kwargs)
        if self.report is None:
            raise ImproperlyConfigured("'{}' must define 'report'".format(self.__class__))

    def get(self, request, *args, **kwargs):
        context = dict(request.GET.lists())
        context.update(kwargs)
        if 'render_pdf_report' in context or 'render_xls_report' in context:
            context.update({'queryset': self.get_queryset()})
            if 'ordering' in context:
                context['ordering'] = context['ordering'].split(',')
            report = self.report()
            if 'render_pdf_report' in request.GET:
                return report.render_pdf_report(context)
            else:
                return report.render_xls_report(context)
        else:
            return super(FilteredListView, self).get(request, *args, **kwargs)