from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    author = filters.NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    # is_favorite = filters.BooleanFilter(
    #     field_name='is_favorite'
    # )
    # is_in_shopping_cart = filters.BooleanFilter(
    #     field_name='is_in_shopping_cart'
    # )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
