from gutils.django.views import CreateView, UpdateView, ListView
from django.core.urlresolvers import reverse_lazy

from gutils.django.views import ProtectedDeleteView
from . import models, forms


# region Países
class PaisesListView(ListView):

    model = models.Pais
    template_name = 'ubicaciones/paises/pais_list.html'


class PaisesCreateView(CreateView):

    model = models.Pais
    form_class = forms.PaisForm
    success_url = reverse_lazy('paises')
    template_name = 'ubicaciones/paises/pais_form.html'


class PaisesUpdateView(UpdateView):

    model = models.Pais
    form_class = forms.PaisForm
    success_url = reverse_lazy('paises')
    template_name = 'ubicaciones/paises/pais_form.html'


class PaisesDeleteView(ProtectedDeleteView):

    model = models.Pais
    success_url = reverse_lazy('paises')
    template_name = 'ubicaciones/paises/pais_confirm_delete.html'
# endregion


# region Provincias
class ProvinciasListView(ListView):

    model = models.Provincia
    template_name = 'ubicaciones/provincias/provincia_list.html'


class ProvinciasCreateView(CreateView):

    model = models.Provincia
    form_class = forms.ProvinciaForm
    success_url = reverse_lazy('provincias')
    template_name = 'ubicaciones/provincias/provincia_form.html'


class ProvinciasUpdateView(UpdateView):

    model = models.Provincia
    form_class = forms.ProvinciaForm
    success_url = reverse_lazy('provincias')
    template_name = 'ubicaciones/provincias/provincia_form.html'


class ProvinciasDeleteView(ProtectedDeleteView):

    model = models.Provincia
    success_url = reverse_lazy('provincias')
    template_name = 'ubicaciones/provincias/provincia_confirm_delete.html'
# endregion


# region Departamentos
class DepartamentosListView(ListView):

    model = models.Departamento
    template_name = 'ubicaciones/departamentos/departamento_list.html'


class DepartamentosCreateView(CreateView):

    model = models.Departamento
    form_class = forms.DepartamentoForm
    success_url = reverse_lazy('departamentos')
    template_name = 'ubicaciones/departamentos/departamento_form.html'


class DepartamentosUpdateView(UpdateView):

    model = models.Departamento
    form_class = forms.DepartamentoForm
    success_url = reverse_lazy('departamentos')
    template_name = 'ubicaciones/departamentos/departamento_form.html'


class DepartamentosDeleteView(ProtectedDeleteView):

    model = models.Departamento
    success_url = reverse_lazy('departamentos')
    template_name = 'ubicaciones/departamentos/departamento_confirm_delete.html'
# endregion


# region Localidades
class LocalidadesListView(ListView):

    model = models.Localidad
    template_name = 'ubicaciones/localidades/localidad_list.html'


class LocalidadesCreateView(CreateView):

    model = models.Localidad
    form_class = forms.LocalidadForm
    success_url = reverse_lazy('localidades')
    template_name = 'ubicaciones/localidades/localidad_form.html'


class LocalidadesUpdateView(UpdateView):

    model = models.Localidad
    form_class = forms.LocalidadForm
    success_url = reverse_lazy('localidades')
    template_name = 'ubicaciones/localidades/localidad_form.html'


class LocalidadesDeleteView(ProtectedDeleteView):

    model = models.Localidad
    success_url = reverse_lazy('localidades')
    template_name = 'ubicaciones/localidades/localidad_confirm_delete.html'
# endregion


# region Direcciones
class DireccionesListView(ListView):

    model = models.Direccion
    template_name = 'ubicaciones/direcciones/direccion_list.html'


class DireccionesCreateView(CreateView):

    model = models.Direccion
    form_class = forms.DireccionForm
    success_url = reverse_lazy('direcciones')
    template_name = 'ubicaciones/direcciones/direccion_form.html'


class DireccionesUpdateView(UpdateView):

    model = models.Direccion
    form_class = forms.DireccionForm
    success_url = reverse_lazy('direcciones')
    template_name = 'ubicaciones/direcciones/direccion_form.html'


class DireccionesDeleteView(ProtectedDeleteView):

    model = models.Direccion
    success_url = reverse_lazy('direcciones')
    template_name = 'ubicaciones/direcciones/direccion_confirm_delete.html'
# endregion
