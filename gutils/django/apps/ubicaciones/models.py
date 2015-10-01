from django.db import models


class Pais(models.Model):

    class Meta:
        verbose_name = 'país'
        verbose_name_plural = 'países'
        ordering = ['nombre', ]

    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    codigo_iso_2 = models.CharField(max_length=2)
    codigo_iso_3 = models.CharField(max_length=3)
    latitud = models.FloatField()
    longitud = models.FloatField()

    def __str__(self):
        return self.nombre


class Provincia(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'provincia'
        verbose_name_plural = 'provincias'
        ordering = ['nombre', ]


class Departamento(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'departamento'
        verbose_name_plural = 'departamentos'
        ordering = ['nombre', ]


class LocalidadManager(models.Manager):

    def get_queryset(self):
        queryset = super(LocalidadManager, self).get_queryset()
        return queryset.select_related('departamento__provincia')


class Localidad(models.Model):
    objects = LocalidadManager()

    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento)
    codigo_postal = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return '{} ({})'.format(self.nombre, self.departamento.provincia.nombre)

    class Meta:
        verbose_name = 'localidad'
        verbose_name_plural = 'localidades'
        ordering = ['nombre', ]


class Direccion(models.Model):

    localidad = models.ForeignKey(Localidad)
    calle = models.CharField(max_length=100)
    numero = models.IntegerField()
    piso = models.CharField(max_length=2, null=True, blank=True)
    division = models.CharField(max_length=2, null=True, blank=True)

    class Meta:
        verbose_name = 'dirección'
        verbose_name_plural = 'direcciones'

    def __str__(self):
        return '{} {} {} {}'.format(self.calle, self.numero, self.piso, self.division)