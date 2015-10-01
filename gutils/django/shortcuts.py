from django.shortcuts import _get_queryset
from django.http import HttpResponse

from gutils.django.core.exceptions import JsonNotFound
from gutils.generic.json import dict_to_json


def get_object_or_json404(klass, *args, **kwargs):
    queryset = _get_queryset(klass)

    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise JsonNotFound()


def render_to_json_response(context, **response_kwargs):
    # returns a JSON response, transforming 'context' to make the payload
    response_kwargs['content_type'] = 'application/json'
    return HttpResponse(dict_to_json(context), **response_kwargs)