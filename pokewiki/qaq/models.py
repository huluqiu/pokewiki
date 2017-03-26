from django.db import models
from django.contrib.postgres.fields import ArrayField


class Gen(models.Model):
    id = models.SmallIntegerField(primary_key=True)


class PokemonClass(models.Model):
    name = models.CharField(max_length=10, primary_key=True)


class EggGroup(models.Model):
    name = models.CharField(max_length=10, primary_key=True)
    description = models.TextField(default='')


class Type(models.Model):
    name = models.CharField(max_length=5, primary_key=True)


class Kind(models.Model):
    name = models.CharField(max_length=5, primary_key=True)


class Stats(models.Model):
    hp = models.SmallIntegerField()
    attack = models.SmallIntegerField()
    defense = models.SmallIntegerField()
    sp_attack = models.SmallIntegerField()
    sp_defense = models.SmallIntegerField()
    speed = models.SmallIntegerField()


class Pokemon(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    gen = models.ForeignKey(
        Gen,
        on_delete=models.CASCADE,
        related_name='pokemons'
    )
    pokemon_class = models.ForeignKey(
        PokemonClass,
        on_delete=models.CASCADE,
        related_name='pokemons'
    )
    name = models.CharField(max_length=10)
    name_jp = models.CharField(max_length=10)
    name_en = models.CharField(max_length=20)
    category = models.CharField(max_length=20)
    egg_step = models.SmallIntegerField()
    egg_groups = models.ManyToManyField(
        EggGroup,
        related_name='pokemons'
    )
    male_rate = models.FloatField()
    female_rate = models.FloatField()
    catch = models.SmallIntegerField()
    happiness = models.SmallIntegerField()
    expto100 = models.IntegerField()
    evolutions = models.ManyToManyField(
        'self',
        through='Evolution',
        symmetrical=False,
        related_name='be_evolutions'
    )
    moves = models.ManyToManyField(
        'Move',
        through='PokemonMove',
        related_name='pokemons'
    )


class PokemonForm(models.Model):
    pokemon = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        related_name='forms',
    )
    name = models.CharField(max_length=20)
    is_normal = models.BooleanField()
    types = models.ManyToManyField(
        Type,
        related_name='forms'
    )
    height = models.FloatField()
    weight = models.FloatField()
    stats = models.ForeignKey(
        Stats,
        on_delete=models.CASCADE,
        related_name='form'
    )
    stats_get = models.ForeignKey(
        Stats,
        on_delete=models.CASCADE,
        related_name='form_get'
    )
    abilities = models.ManyToManyField(
        'Ability',
        through='PokemonAbility',
        related_name='forms'
    )

    class Meta:
        unique_together = (('pokemon', 'name'))


class Evolution(models.Model):
    evolution_from = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        related_name='as_evolution_from_set',
    )
    evolution_to = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        related_name='as_evolution_to_set',
    )
    way = models.CharField(max_length=20)
    condition = models.TextField()


class Ability(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    gen = models.ForeignKey(
        Gen,
        on_delete=models.CASCADE,
        related_name='abilities'
    )
    name = models.CharField(max_length=10)
    name_jp = models.CharField(max_length=10)
    name_en = models.CharField(max_length=20)
    effect = models.TextField()
    effect_battle = models.TextField()
    effect_map = models.TextField()


class PokemonAbility(models.Model):
    pokemon_form = models.ForeignKey(
        PokemonForm,
        on_delete=models.CASCADE,
    )
    ability = models.ForeignKey(
        Ability,
        on_delete=models.CASCADE,
    )
    is_hidden = models.BooleanField()


class Move(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    gen = models.ForeignKey(
        Gen,
        on_delete=models.CASCADE,
        related_name='moves'
    )
    name = models.CharField(max_length=10)
    name_jp = models.CharField(max_length=20)
    name_en = models.CharField(max_length=30)
    type = models.ForeignKey(
        Type,
        on_delete=models.CASCADE,
        related_name='moves'
    )
    kind = models.ForeignKey(
        Kind,
        on_delete=models.CASCADE,
        related_name='moves'
    )
    power = models.SmallIntegerField()
    accuracy = models.SmallIntegerField()
    pp = models.SmallIntegerField()
    effect = models.TextField()
    effect_battle = models.TextField()
    effect_map = models.TextField()
    priority = models.SmallIntegerField()
    z_stone = models.CharField(max_length=10)
    z_move = models.CharField(max_length=10)
    z_power = models.CharField(max_length=20)


class PokemonMove(models.Model):
    pokemon = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
    )
    move = models.ForeignKey(
        Move,
        on_delete=models.CASCADE,
    )
    way = models.CharField(max_length=20)
    condition = models.CharField(max_length=10)


class Router(models.Model):
    uri = models.CharField(max_length=100)
    flag = models.CharField(max_length=10)
    cns = ArrayField(
        models.CharField(max_length=10),
    )
