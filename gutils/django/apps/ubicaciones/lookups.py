from gutils.django.forms.typeahead.lookups import Lookup, register_lookup

from .models import Localidad


class LocalidadLookup(Lookup):
    model = Localidad
    search_fields = ['nombre', 'departamento__provincia__nombre']


register_lookup(LocalidadLookup)