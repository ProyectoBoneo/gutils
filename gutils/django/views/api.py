import json

from django.core.urlresolvers import reverse

from rest_framework import views
from rest_framework.response import Response


class UrlReversingView(views.APIView):

    def get(self, request):
        request_datastring = request.GET.get('json_data', None)
        request_data = json.loads(request_datastring)
        url_name = request_data.get('url_name', None)
        args = request_data.get('args', None)
        kwargs = {}
        reverse_kwargs = {}
        if args:
            reverse_kwargs['args'] = args
        if kwargs:
            reverse_kwargs['kwargs'] = kwargs
        response_context = {'url': reverse(url_name, **reverse_kwargs)}
        return Response(response_context)