from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from users.models import User, Follow
from recipes.models import Tags, Ingredients, Recipes, Favorite, ShoppingCart
from .permissions import IsAdminOrReadOnly, IsAdminAuthorOrReadOnly
from .serializers import TagSerializer, IngredientsSerializer, RecipesSerializer, UsersSerializer, FollowSerializer, \
    FavoriteSerializer, CreateRecipesSerializer, ShoppingCartSerializer, InfoFollowSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)
    # filter_backends


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(['get'], detail=False)
    def subscriptions(self, request):
        user_obj = User.objects.filter(following__user=request.user)
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(user_obj, request)
        serializer = InfoFollowSerializer(
            result_page, many=True, context={"current_user": request.user}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(['POST', 'DELETE'], detail=True)
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        subscription = get_object_or_404(
            Follow,
            author=author,
            user=request.user.pk
        )
        data = {'user': request.user.pk, 'author': pk}
        if request.method == 'POST':
            serializer = FollowSerializer(
                data=data,
                author=author
            )
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipesViewSet(viewsets.ModelViewSet):
    """
    Вью для рецептов.
    """
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = (IsAdminAuthorOrReadOnly,)
    #  filter_backend

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipesSerializer
        return CreateRecipesSerializer

    @action(['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        favorite = get_object_or_404(
            Favorite,
            user=request.user,
            recipe=recipe
        )
        data = {'user': request.user.id, 'recipe': pk}
        context = {'request': request}
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data=data,
                context=context
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        shopping_cart = get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=recipe
        )
        data = {'user': request.user.id, 'recipe': pk}
        context = {'request': request}
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data=data,
                context=context
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
