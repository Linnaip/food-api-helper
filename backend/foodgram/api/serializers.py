from rest_framework import serializers

from ..recipes.models import Tags, Ingredients


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = '__all__'
        lookup_field = 'slug'


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'
