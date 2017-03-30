from rest_framework import serializers
from qaq.models import Pokemon, EggGroup


class PokemonListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pokemon
        fields = ('url', 'id', 'name', 'name_jp', 'name_en')


class PokemonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pokemon
        fields = ('id', 'name', 'name_jp', 'name_en', 'egg_groups')


class EggGroupSerializer(serializers.HyperlinkedModelSerializer):
    pokemon_set = serializers.HyperlinkedRelatedField(many=True, view_name='pokemon-detail', read_only=True)

    class Meta:
        model = EggGroup
        fields = ('name', 'description', 'pokemon_set')


class DomainCellSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=10)
    uri = serializers.CharField(max_length=100)
    flag = serializers.CharField(max_length=5)
