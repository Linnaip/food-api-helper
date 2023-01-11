from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    """Фильтр рецептов по автору/тегу/подписке/наличию в списке покупок"""
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    author = filters.NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(in_favorite__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(is_shopping_cart__user=user)
        return queryset
