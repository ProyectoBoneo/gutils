import re
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db.models import Q

REGISTERED_LOOKUPS = []


class Lookup:
    """
    To use this class, you must either define model or get_base_queryset()
    Specifications:
    ---> display: it's a function that returns the string representation
             the typeahead will show
    ---> search_fields: it's a list of fields to be used in the query. If left empty,
             filtering will be done in python
    ---> clean_querystring: it's a function that cleans the querystring of
             additional characters added by the display
    """
    form_class = None
    model_description = None
    template_name = None
    model = None
    search_fields = []
    display = lambda x: str(x)

    @classmethod
    def get_form_class(cls):
        return cls.form_class

    @classmethod
    def save_model(cls, form):
        return form.save()

    @classmethod
    def clean_querystring(cls, querystring):
        if cls.search_fields:
            querystring = re.sub(r'[^ a-zA-Z0-9]', '', querystring)
            querystring = re.sub(r'[ ]+', ' ', querystring)
        return querystring

    @classmethod
    def get_base_queryset(cls):
        if cls.model is not None:
            return cls.model.objects.all()
        else:
            raise ImproperlyConfigured("'{}' must define model or override get_base_queryset".format(cls.__name__))

    @classmethod
    def get_model_description(cls):
        if cls.model_description is not None:
            return cls.model_description
        else:
            return cls.get_model().__name__

    @classmethod
    def get_model(cls):
        if cls.model is not None:
            return cls.model
        else:
            queryset = cls.get_base_queryset()
            if queryset is not None:
                return queryset.model
            else:
                raise ImproperlyConfigured("'{}' get_base_queryset doesn't provide a queryset".format(cls.__name__))

    @classmethod
    def get_object(cls, pk):
        try:
            return cls.get_base_queryset().get(pk=pk)
        except (ObjectDoesNotExist, ValueError):
            return None

    @classmethod
    def get_object_description(cls, pk):
        obj = cls.get_object(pk)
        if obj:
            return cls.display(obj)
        else:
            return ''

    @classmethod
    def py_filter(cls, queryset, search_list):
        instances = []
        for instance in queryset:
            display = cls.display(instance).lower()
            if not [term for term in search_list if term.lower() not in display]:
                instances.append(instance)
        return instances

    @classmethod
    def db_filter(cls, queryset, search_list):
        query_object = None
        for search_term in search_list:
            query_for_term = None
            for idx, field in enumerate(cls.search_fields):
                kwarg = {'{}__icontains'.format(field): search_term}
                new_q = Q(**kwarg)
                if query_for_term is None:
                    query_for_term = new_q
                else:
                    query_for_term = query_for_term | new_q
            if query_object is None:
                query_object = query_for_term
            else:
                query_object = query_object & query_for_term
        if query_object:
            queryset = queryset.filter(query_object)
        return queryset

    @classmethod
    def get_filtered_queryset(cls, querystring):
        queryset = cls.get_base_queryset()
        if queryset is None:
            raise ImproperlyConfigured("'{}' get_base_queryset doesn't provide a queryset".format(cls.__name__))
        if querystring is not None:
            querystring = cls.clean_querystring(querystring)
            if querystring.strip() != '':
                search_list = [t.strip() for t in querystring.split(' ')]
                if cls.search_fields:
                    queryset = cls.db_filter(queryset, search_list)
                else:
                    queryset = cls.py_filter(queryset, search_list)
        return queryset


def register_lookup(klass):
    if klass.__name__ in [c.__name__ for c in REGISTERED_LOOKUPS]:
        raise ImproperlyConfigured("A class with name '{}' has been registered as a lookup")
    REGISTERED_LOOKUPS.append(klass)
