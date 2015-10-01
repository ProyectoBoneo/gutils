from django.db.models import Model
import json
import datetime


def get_serializable_obj(obj):
    if isinstance(obj, datetime.date):
        return obj.__format__("%d/%m/%Y")
    elif isinstance(obj, datetime.datetime):
        return obj.__format__("%d/%m/%Y %H:%M:%S")
    elif isinstance(obj, Model):
        if hasattr(obj, 'pk'):
            return obj.pk
        else:
            return None
    else:
        return None


def dict_to_json(dictionary):
    return json.dumps(dictionary, default=get_serializable_obj)


def json_to_dict(json_string):
    return json.loads(json_string)