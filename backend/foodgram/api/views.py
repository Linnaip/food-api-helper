from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .pagintation import CustomPagination
from .permissions import IsAdminAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (CreateRecipesSerializer, FavoriteSerializer,
                          FollowSerializer, IngredientsSerializer, RecipesSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UsersSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backend = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    @action(detail=False)
    def subscriptions(self, request):
        user = request.user
        follows = User.objects.filter(following__user=user)
        page = self.paginate_queryset(follows)
        serializer = FollowSerializer(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'],
            detail=True, )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Follow.objects.filter(
            user=user, author=author)

        if request.method == 'POST':
            if subscription.exists():
                return Response({'error': 'Вы уже подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response({'error': 'Невозможно подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(author, context={'request': request})
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Вы не подписаны на этого пользователя'},
                            status=status.HTTP_400_BAD_REQUEST)


class RecipesViewSet(viewsets.ModelViewSet):
    """
    Вью для рецептов.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipesSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAdminAuthorOrReadOnly,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST', 'PATCH']:
            return CreateRecipesSerializer
        return RecipesSerializer

    @staticmethod
    def post_delete_method(request, model, serializer_name, pk):
        """
        Функция для favorite and shopping_cart.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        data = {'user': request.user.id, 'recipe': pk}
        context = {'request': request}
        if request.method == 'POST':
            serializer = serializer_name(
                data=data,
                context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            model_object = get_object_or_404(
                model,
                user=request.user,
                recipe=recipe
            )
            model_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        return self.post_delete_method(
            request=request,
            model=Favorite,
            serializer_name=FavoriteSerializer,
            pk=pk
        )

    @action(['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        return self.post_delete_method(
            request=request,
            model=ShoppingCart,
            serializer_name=ShoppingCartSerializer,
            pk=pk
        )

    @action(['GET'], detail=False)
    def download_shopping_cart(self, request):
        shopping_cart = []
        cart = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcart__user=request.user.id
            ).values(
                "ingredients__name",
                "ingredients__measurement_unit",
            ).annotate(total_quantity=Sum("amount"))
        )
        for item in cart:
            name = item["ingredients__name"]
            measurement_unit = item["ingredients__measurement_unit"]
            quantity = item["total_quantity"]
            shopping_cart.append(f"{name}: {quantity} {measurement_unit}")
        content = "\n".join(shopping_cart)
        content_type = "text/plain,charset=utf8"
        response = HttpResponse(content, content_type=content_type)
        response[
            "Content-Disposition"
        ] = f"attachment; filename={'shopping_list.txt'}"
        return response
