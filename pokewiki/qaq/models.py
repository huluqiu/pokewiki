from django.db import models
from django.contrib.postgres.fields import JSONField


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


class Pokemon(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    gen = models.ForeignKey(Gen, on_delete=models.CASCADE)
    pokemon_class = models.ForeignKey(PokemonClass, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    name_jp = models.CharField(max_length=10)
    name_en = models.CharField(max_length=20)
    category = models.CharField(max_length=20)
    egg_step = models.SmallIntegerField()
    egg_groups = models.ManyToManyField(EggGroup)
    male_rate = models.FloatField()
    female_rate = models.FloatField()
    catch = models.SmallIntegerField()
    happiness = models.SmallIntegerField()
    expto100 = models.IntegerField()
    evolutions = models.ManyToManyField(
        'self',
        through='Evolution',
        symmetrical=False
    )
    moves = models.ManyToManyField('Move', through='PokemonMove')


class PokemonForm(models.Model):
    pokemon = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        related_name='pokemonforms',
    )
    form = models.CharField(max_length=20)
    is_normal = models.BooleanField()
    types = models.ManyToManyField(Type)
    height = models.FloatField()
    weight = models.FloatField()
    stats = JSONField()
    stats_get = JSONField()
    abilities = models.ManyToManyField('Ability', through='PokemonAbility')

    class Meta:
        unique_together = (('pokemon', 'form'))


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
    gen = models.ForeignKey(Gen, on_delete=models.CASCADE)
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
    gen = models.ForeignKey(Gen, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    name_jp = models.CharField(max_length=20)
    name_en = models.CharField(max_length=30)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    kind = models.ForeignKey(Kind, on_delete=models.CASCADE)
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


class WordDic(models.Model):
    word = models.CharField(max_length=10, primary_key=True)
    tag = models.CharField(max_length=10)
