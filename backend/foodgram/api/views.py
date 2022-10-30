from django.shortcuts import render
from rest_framework import viewsets

from .serializers import TagSerializer, IngredientsSerializer
from ..recipes.models import Tags, Ingredients


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
