# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-04 06:51
from __future__ import unicode_literals

from django.db import migrations


def load_gen(apps, schema_editor):
    Gen = apps.get_model('qaq', 'Gen')
    gens = [Gen(num=gen) for gen in range(1, 8)]
    Gen.objects.bulk_create(gens)


def load_class(apps, schema_editor):
    PokemonClass = apps.get_model('qaq', 'PokemonClass')


class Migration(migrations.Migration):

    dependencies = [
        ('qaq', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_gen, load_class),
    ]
