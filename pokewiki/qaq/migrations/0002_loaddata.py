# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-05 14:41
from __future__ import unicode_literals

from django.db import migrations
from qaq.core import scrub


def load_gen(apps, schema_editor):
    Gen = apps.get_model('qaq', 'Gen')
    gens = [Gen(id=gen) for gen in scrub.get_gens()]
    Gen.objects.bulk_create(gens)


def load_class(apps, schema_editor):
    PokemonClass = apps.get_model('qaq', 'PokemonClass')
    pcs = [PokemonClass(name=c)
           for c in scrub.get_pokemon_class()]
    PokemonClass.objects.bulk_create(pcs)


def load_egg_group(apps, schema_editorl):
    EggGroup = apps.get_model('qaq', 'EggGroup')
    egg_groups = [EggGroup(name=n, description=des)
                  for (n, des) in scrub.get_egg_groups()]
    EggGroup.objects.bulk_create(egg_groups)


def load_type(apps, schema_editor):
    Type = apps.get_model('qaq', 'Type')
    types = [Type(name=n) for n in scrub.get_types()]
    Type.objects.bulk_create(types)


def load_kind(apps, schema_editor):
    Kind = apps.get_model('qaq', 'Kind')
    kinds = [Kind(name=n) for n in scrub.get_kinds()]
    Kind.objects.bulk_create(kinds)


def load_pokemon(apps, schema_editor):
    Pokemon = apps.get_model('qaq', 'Pokemon')
    Gen = apps.get_model('qaq', 'Gen')
    PokemonClass = apps.get_model('qaq', 'PokemonClass')
    EggGroup = apps.get_model('qaq', 'EggGroup')
    for v in scrub.get_pokemons():
        (num, name, name_jp, name_en, pokemon_class,
         category, egg_groups, eggStep, male_rate,
         female_rate, catch, happiness, expto100, gen) = v
        gen = Gen.objects.get(pk=gen)
        pokemon_class = PokemonClass.objects.get(pk=pokemon_class)
        pokemon = Pokemon(
            id=num,
            gen=gen,
            pokemon_class=pokemon_class,
            name=name,
            name_jp=name_jp,
            name_en=name_en,
            category=category,
            egg_step=eggStep,
            male_rate=male_rate,
            female_rate=female_rate,
            catch=catch,
            happiness=happiness,
            expto100=expto100
        )
        pokemon.save()
        egg_groups = EggGroup.objects.filter(name__in=egg_groups)
        pokemon.egg_groups.add(*egg_groups)


def load_form(apps, schema_editor):
    def stats_map(stats):
        d = {}
        keys = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
        for i, v in enumerate(stats):
            d[keys[i]] = v
        return d

    PokemonForm = apps.get_model('qaq', 'PokemonForm')
    Pokemon = apps.get_model('qaq', 'Pokemon')
    Type = apps.get_model('qaq', 'Type')
    for v in scrub.get_forms():
        (num, form_name, types, height, weight,
         stats, stats_get, is_normal) = v
        pokemon = Pokemon.objects.get(pk=num)
        stats = stats_map(stats)
        stats_get = stats_map(stats_get)
        types = Type.objects.filter(name__in=types)
        try:
            obj = PokemonForm.objects.get(pokemon=pokemon, form=form_name)
        except PokemonForm.DoesNotExist:
            obj = PokemonForm(
                pokemon=pokemon,
                form=form_name,
                is_normal=is_normal,
                height=height,
                weight=weight,
                stats=stats,
                stats_get=stats_get
            )
            obj.save()
            obj.types.add(*types)


def load_evolution(apps, schema_editor):
    Evolution = apps.get_model('qaq', 'Evolution')
    Pokemon = apps.get_model('qaq', 'Pokemon')
    evolutions = []
    for (e_from, e_to, way, condition) in scrub.get_evolutions():
        evolution_from = Pokemon.objects.get(pk=e_from)
        evolution_to = Pokemon.objects.get(pk=e_to)
        evlution = Evolution(
            evolution_from=evolution_from,
            evolution_to=evolution_to,
            way=way,
            condition=condition
        )
        evolutions.append(evlution)
    Evolution.objects.bulk_create(evolutions)


def load_ability(apps, schema_editor):
    Ability = apps.get_model('qaq', 'Ability')
    Gen = apps.get_model('qaq', 'Gen')
    abilities = []
    for v in scrub.get_abilities():
        (num, name, name_jp, name_en, effect, effect_battle,
         effect_map, gen) = v
        gen = Gen.objects.get(pk=gen)
        ability = Ability(
            id=num,
            gen=gen,
            name=name,
            name_jp=name_jp,
            name_en=name_en,
            effect=effect,
            effect_battle=effect_battle,
            effect_map=effect_map
        )
        abilities.append(ability)
    Ability.objects.bulk_create(abilities)


def load_pokemon_ability(apps, schema_editor):
    PokemonAbility = apps.get_model('qaq', 'PokemonAbility')
    Ability = apps.get_model('qaq', 'Ability')
    PokemonForm = apps.get_model('qaq', 'PokemonForm')
    pokemon_abilities = []
    for (poke_num, ability_num, form_name, is_hidden) in scrub.get_pokemon_ability_map():
        pokemon_form = PokemonForm.objects.get(pokemon=poke_num, form=form_name)
        ability = Ability.objects.get(pk=ability_num)
        pokemon_ability = PokemonAbility(
            pokemon_form=pokemon_form,
            ability=ability,
            is_hidden=is_hidden
        )
        pokemon_abilities.append(pokemon_ability)
    PokemonAbility.objects.bulk_create(pokemon_abilities)


def load_move(apps, schema_editor):
    Move = apps.get_model('qaq', 'Move')
    Gen = apps.get_model('qaq', 'Gen')
    Type = apps.get_model('qaq', 'Type')
    Kind = apps.get_model('qaq', 'Kind')
    moves = []
    for v in scrub.get_moves():
        (num, name, name_jp, name_en, type, kind, power,
         accuracy, pp, effect, effect_battle, effect_map,
         priority, gen, z_stone, z_move, z_power) = v
        gen = Gen.objects.get(pk=gen)
        type = Type.objects.get(pk=type)
        kind = Kind.objects.get(pk=kind)
        move = Move(
            id=num,
            gen=gen,
            name=name,
            name_jp=name_jp,
            name_en=name_en,
            type=type,
            kind=kind,
            power=power,
            accuracy=accuracy,
            pp=pp,
            effect=effect,
            effect_battle=effect_battle,
            effect_map=effect_map,
            priority=priority,
            z_stone=z_stone,
            z_move=z_move,
            z_power=z_power
        )
        moves.append(move)
    Move.objects.bulk_create(moves)


def load_pokemon_move(apps, schema_editor):
    PokemonMove = apps.get_model('qaq', 'PokemonMove')
    Pokemon = apps.get_model('qaq', 'Pokemon')
    Move = apps.get_model('qaq', 'Move')
    pokemon_moves = []
    for (poke_num, move_num, way, condition, form) in scrub.get_pokemon_move_map():
        pokemon = Pokemon.objects.get(pk=poke_num)
        move = Move.objects.get(pk=move_num)
        pokemon_move = PokemonMove(
            pokemon=pokemon,
            move=move,
            way=way,
            condition=condition
        )
        pokemon_moves.append(pokemon_move)
    PokemonMove.objects.bulk_create(pokemon_moves)


class Migration(migrations.Migration):

    dependencies = [
        ('qaq', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_gen),
        migrations.RunPython(load_class),
        migrations.RunPython(load_egg_group),
        migrations.RunPython(load_type),
        migrations.RunPython(load_kind),
        migrations.RunPython(load_pokemon),
        migrations.RunPython(load_form),
        migrations.RunPython(load_evolution),
        migrations.RunPython(load_ability),
        migrations.RunPython(load_pokemon_ability),
        migrations.RunPython(load_move),
        migrations.RunPython(load_pokemon_move),
    ]