from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework.response import Response

from .serializers import TagSerializer, IngredientsSerializer, RecipesSerializer, UsersSerializer, FollowSerializer
from recipes.models import Tags, Ingredients, Recipes
from users.models import User, Follow


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    @action(['get'], detail=False)
    def subscriptions(self, request):
        follow = Follow.objects.filter(user=request.user)
        serializer = FollowSerializer(follow, many=True)
        return Response(serializer.data)

    @action(['POST', 'DELETE'], detail=True)
    def subscribe(self, request, pk):
        subscription = get_object_or_404(
            Follow,
            author=get_object_or_404(User, id=pk),
            user=request.user
        )
        if request.method == 'POST':
            serializer = FollowSerializer(
                data=request.data
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
