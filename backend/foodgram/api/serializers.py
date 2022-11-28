from rest_framework import serializers

from recipes.models import Tags, Ingredients, Recipes, Favorite, ShoppingCart
from users.models import User, Follow


class UsersSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email',
            'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = (
            'id', 'name',
            'color', 'slug'
        )


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'


class RecipesSerializer(serializers.ModelSerializer):
    tag = TagSerializer(read_only=True, many=True)
    ingredients = IngredientsSerializer(read_only=True, many=True)
    author = UsersSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipes
        fields = (
            'ingredients', 'tag',
            'image', 'name',
            'text', 'cooking_time', 'author',
            'is_favorite', 'is_in_shopping_cart'
        )

    def get_is_favorite(self, obj):
        # Рефакторинг хард кодинга нужно сделать!
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        # Повтор кода
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user, recipe__id=obj.id).exists()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'

    def validate_following(self, following):
        if self.context.get('request').user == following:
            raise serializers.ValidationError(
                'You cant follow to yourself.'
            )
        return following
