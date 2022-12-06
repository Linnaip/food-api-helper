from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import viewsets, status
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework.response import Response
from weasyprint import HTML

from .serializers import TagSerializer, IngredientsSerializer, RecipesSerializer, UsersSerializer, FollowSerializer,\
    FavoriteSerializer, CreateRecipesSerializer, ShoppingCartSerializer
from recipes.models import Tags, Ingredients, Recipes, Favorite, ShoppingCart, RecipeIngredients
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
    """
    Вью для рецептов.
    """
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer

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

    def download_shopping_cart(self, request):
        """
        Вью для скачивания списка.
        """
        shopping_list = RecipeIngredients.objects.filter(
            recipe__cart__user=request.user
        ).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount')).values_list(
            'ingredients__name', 'quantity', 'ingredients__measurement_unit'
        )
        html_template = render_to_string('recipes/pdf_template.html',
                                         {'ingredients': shopping_list})
        html = HTML(string=html_template)
        result = html.write_pdf()
        response = HttpResponse(result, content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=shopping_list.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        return response
