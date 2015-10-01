from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = patterns('',
                       url(r'^paises/$',
                           login_required(views.PaisesListView.as_view()),
                           name='paises'),

                       url(r'^paises/nuevo/$',
                           login_required(views.PaisesCreateView.as_view()),
                           name='nuevo_pais'),

                       url(r'^paises/editar/(?P<pk>\d+)/$',
                           login_required(views.PaisesUpdateView.as_view()),
                           name='editar_pais'),

                       url(r'^paises/eliminar/(?P<pk>\d+)/$',
                           login_required(views.PaisesDeleteView.as_view()),
                           name='eliminar_pais'),

                       url(r'^provincias/$',
                           login_required(views.ProvinciasListView.as_view()),
                           name='provincias'),

                       url(r'^provincias/nuevo/$',
                           login_required(views.ProvinciasCreateView.as_view()),
                           name='nuevo_provincia'),

                       url(r'^provincias/editar/(?P<pk>\d+)/$',
                           login_required(views.ProvinciasUpdateView.as_view()),
                           name='editar_provincia'),

                       url(r'^provincias/eliminar/(?P<pk>\d+)/$',
                           login_required(views.ProvinciasDeleteView.as_view()),
                           name='eliminar_provincia'),
                       
                       url(r'^departamentos/$',
                           login_required(views.DepartamentosListView.as_view()),
                           name='departamentos'),

                       url(r'^departamentos/nuevo/$',
                           login_required(views.DepartamentosCreateView.as_view()),
                           name='nuevo_departamento'),

                       url(r'^departamentos/editar/(?P<pk>\d+)/$',
                           login_required(views.DepartamentosUpdateView.as_view()),
                           name='editar_departamento'),

                       url(r'^departamentos/eliminar/(?P<pk>\d+)/$',
                           login_required(views.DepartamentosDeleteView.as_view()),
                           name='eliminar_departamento'),
                       
                       url(r'^localidades/$',
                           login_required(views.LocalidadesListView.as_view()),
                           name='localidades'),

                       url(r'^localidades/nuevo/$',
                           login_required(views.LocalidadesCreateView.as_view()),
                           name='nuevo_localidad'),

                       url(r'^localidades/editar/(?P<pk>\d+)/$',
                           login_required(views.LocalidadesUpdateView.as_view()),
                           name='editar_localidad'),

                       url(r'^localidades/eliminar/(?P<pk>\d+)/$',
                           login_required(views.LocalidadesDeleteView.as_view()),
                           name='eliminar_localidad'),
                       )
