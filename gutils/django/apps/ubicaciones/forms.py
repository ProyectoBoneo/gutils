from gutils.django.forms import BaseModelForm

from .models import Pais, Provincia, Departamento, Localidad, Direccion


class PaisForm(BaseModelForm):

    class Meta:
        exclude = []
        model = Pais


class ProvinciaForm(BaseModelForm):

    class Meta:
        exclude = []
        model = Provincia
        labels = {'pais': 'País', }


class DepartamentoForm(BaseModelForm):

    class Meta:
        exclude = []
        model = Departamento


class LocalidadForm(BaseModelForm):

    class Meta:
        exclude = []
        model = Localidad


class DireccionForm(BaseModelForm):

    class Meta:
        exclude = []
        model = Direccion
        labels = {'numero': 'Número', 'division': 'División', 'codigo_postal': 'Código postal', }