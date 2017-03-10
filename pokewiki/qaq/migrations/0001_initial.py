# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-05 14:39
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ability',
            fields=[
                ('id', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10)),
                ('name_jp', models.CharField(max_length=10)),
                ('name_en', models.CharField(max_length=20)),
                ('effect', models.TextField()),
                ('effect_battle', models.TextField()),
                ('effect_map', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='EggGroup',
            fields=[
                ('name', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('description', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Evolution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('way', models.CharField(max_length=20)),
                ('condition', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Gen',
            fields=[
                ('id', models.SmallIntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Kind',
            fields=[
                ('name', models.CharField(max_length=5, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Move',
            fields=[
                ('id', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10)),
                ('name_jp', models.CharField(max_length=20)),
                ('name_en', models.CharField(max_length=30)),
                ('power', models.SmallIntegerField()),
                ('accuracy', models.SmallIntegerField()),
                ('pp', models.SmallIntegerField()),
                ('effect', models.TextField()),
                ('effect_battle', models.TextField()),
                ('effect_map', models.TextField()),
                ('priority', models.SmallIntegerField()),
                ('z_stone', models.CharField(max_length=10)),
                ('z_move', models.CharField(max_length=10)),
                ('z_power', models.CharField(max_length=20)),
                ('gen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qaq.Gen')),
                ('kind', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qaq.Kind')),
            ],
        ),
        migrations.CreateModel(
            name='Pokemon',
            fields=[
                ('id', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10)),
                ('name_jp', models.CharField(max_length=10)),
                ('name_en', models.CharField(max_length=20)),
                ('category', models.CharField(max_length=20)),
                ('egg_step', models.SmallIntegerField()),
                ('male_rate', models.FloatField()),
                ('female_rate', models.FloatField()),
                ('catch', models.SmallIntegerField()),
                ('happiness', models.SmallIntegerField()),
                ('expto100', models.IntegerField()),
                ('egg_groups', models.ManyToManyField(to='qaq.EggGroup')),
                ('evolutions', models.ManyToManyField(through='qaq.Evolution', to='qaq.Pokemon')),
                ('gen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qaq.Gen')),
            ],
        ),
        migrations.CreateModel(
            name='PokemonAbility',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_hidden', models.BooleanField()),
                ('ability', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qaq.Ability')),
            ],
        ),
        migrations.CreateModel(
            name='PokemonClass',
            fields=[
                ('name', models.CharField(max_length=10, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='PokemonForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form', models.CharField(max_length=20)),
                ('is_normal', models.BooleanField()),
                ('height', models.FloatField()),
                ('weight', models.FloatField()),
                ('stats', django.contrib.postgres.fields.jsonb.JSONField()),
                ('stats_get', django.contrib.postgres.fields.jsonb.JSONField()),
                ('abilities', models.ManyToManyField(through='qaq.PokemonAbility', to='qaq.Ability')),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qaq.Pokemon')),
            ],
        ),
        migrations.CreateModel(
            name='PokemonMove',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('way', models.CharField(max_length=20)),
                ('condition', models.CharField(max_length=10)),
                ('move', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qaq.Move')),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qaq.Pokemon')),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('name', models.CharField(max_length=5, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='pokemonform',
            name='types',
            field=models.ManyToManyField(to='qaq.Type'),
        ),
        migrations.AddField(
            model_name='pokemonability',
            name='pokemon_form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qaq.PokemonForm'),
        ),
        migrations.AddField(
            model_name='pokemon',
            name='moves',
            field=models.ManyToManyField(through='qaq.PokemonMove', to='qaq.Move'),
        ),
        migrations.AddField(
            model_name='pokemon',
            name='pokemon_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qaq.PokemonClass'),
        ),
        migrations.AddField(
            model_name='move',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qaq.Type'),
        ),
        migrations.AddField(
            model_name='evolution',
            name='evolution_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='as_evolution_from_set', to='qaq.Pokemon'),
        ),
        migrations.AddField(
            model_name='evolution',
            name='evolution_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='as_evolution_to_set', to='qaq.Pokemon'),
        ),
        migrations.AddField(
            model_name='ability',
            name='gen',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qaq.Gen'),
        ),
        migrations.AlterUniqueTogether(
            name='pokemonform',
            unique_together=set([('pokemon', 'form')]),
        ),
    ]