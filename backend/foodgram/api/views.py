from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action

from .serializers import TagSerializer, IngredientsSerializer, RecipesSerializer, UsersSerializer
from recipes.models import Tags, Ingredients, Recipes
from users.models import User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
