# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['nombre'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Direccion',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('calle', models.CharField(max_length=100)),
                ('numero', models.IntegerField()),
                ('piso', models.CharField(null=True, max_length=2, blank=True)),
                ('division', models.CharField(null=True, max_length=2, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Localidad',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('codigo_postal', models.CharField(null=True, max_length=10, blank=True)),
                ('departamento', models.ForeignKey(to='ubicaciones.Departamento')),
            ],
            options={
                'ordering': ['nombre'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('codigo_iso_2', models.CharField(max_length=2)),
                ('codigo_iso_3', models.CharField(max_length=3)),
                ('latitud', models.FloatField()),
                ('longitud', models.FloatField()),
            ],
            options={
                'ordering': ['nombre'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('pais', models.ForeignKey(to='ubicaciones.Pais')),
            ],
            options={
                'ordering': ['nombre'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='direccion',
            name='localidad',
            field=models.ForeignKey(to='ubicaciones.Localidad'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='departamento',
            name='provincia',
            field=models.ForeignKey(to='ubicaciones.Provincia'),
            preserve_default=True,
        ),
    ]
