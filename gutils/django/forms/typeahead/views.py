from django.shortcuts import Http404, render_to_response, RequestContext

from gutils.django.views import View
from gutils.django.shortcuts import render_to_json_response
from gutils.django.forms.typeahead.lookups import REGISTERED_LOOKUPS


class TypeaheadAddModelView(View):

    lookup_not_found = Http404("Couldn't find lookup")

    def get_lookup(self, kwargs):
        lookup_name = kwargs.get('lookup_name', None)
        if lookup_name is not None:
            try:
                return [l for l in REGISTERED_LOOKUPS if l.__name__ == lookup_name][0]
            except IndexError:
                return None

    def get_template_name(self, lookup):
        if lookup.template_name is None:
            return 'typeahead/add_model_form.html'
        else:
            return lookup.template_name

    def get(self, request, *args, **kwargs):
        lookup = self.get_lookup(kwargs)
        if lookup is None:
            return self.lookup_not_found
        context = {'form': lookup.get_form_class()()}
        return render_to_response(self.get_template_name(lookup), context, context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        lookup = self.get_lookup(kwargs)
        if lookup is None:
            return self.lookup_not_found
        form = lookup.get_form_class()(request.POST)
        context = {'form': form, }
        if form.is_valid():
            new_instance = lookup.save_model(form)
            context = {'valid': True, 'instance_id': new_instance.pk}
            return render_to_json_response(context)
        else:
            return render_to_response(self.get_template_name(lookup), context, context_instance=RequestContext(request))


class TypeaheadView(View):

    def get(self, request):
        context = None
        lookup_name = request.GET.get('lookup', None)
        querystring = request.GET.get('query', None)
        form_input_value = request.GET.get('form_input_value', None)
        if lookup_name is not None:
            lookup = [l for l in REGISTERED_LOOKUPS if l.__name__ == lookup_name][0]
            if querystring is not None:
                context = []
                queryset = lookup.get_filtered_queryset(querystring)
                for instance in queryset:
                    context.append({'id': instance.pk,
                                    'description': lookup.display(instance)})
            elif form_input_value is not None:
                instance = lookup.get_object(form_input_value)
                if instance is not None:
                    display = lookup.display(instance)
                else:
                    display = ''
                context = {'description': display}
        return render_to_json_response(context)
