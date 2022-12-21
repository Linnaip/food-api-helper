from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import Follow, User

CONSTANT = 6


class CreateUsersSerializer(UserCreateSerializer):
    """
    Для создания юзера.
    """

    class Meta:
        model = User
        fields = (
            'id', 'email',
            'username', 'first_name', 'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UsersSerializer(UserSerializer):
    """
    Отображает пользователя.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email',
            'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj: User):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id', 'name',
            'color', 'slug'
        )


class IngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientInRecipesSerializer(serializers.ModelSerializer):
    """
    Выводит информацию о ингредиентах в рецептах
    """
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name',
            'measurement_unit', 'amount',
        )


class ShortInfoRecipesSerializer(serializers.ModelSerializer):
    """
    Вывод краткой информации о рецепте
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CreateIngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Для создания ингредиетов.
    """
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )

    def create(self, validated_data):
        return RecipeIngredient.objects.create(
            ingredients=validated_data.get('id'),
            amount=validated_data.get('amount')
        )


class CreateRecipesSerializer(serializers.ModelSerializer):
    """
    Для создания рецептов.
    """
    image = Base64ImageField(use_url=True, max_length=None)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = CreateIngredientRecipeSerializer(many=True)
    author = UsersSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'tags',
            'image', 'name', 'text',
            'cooking_time', 'ingredients'
        )

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredients=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient.get('amount'),
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients_data = validated_data.pop('ingredients')
        tag_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data,
        )
        recipe.tags.set(tag_data)
        self.create_ingredients(ingredients=ingredients_data, recipe=recipe)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop("ingredients")
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients, recipe)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        rep_data = self.context.get('request')
        return RecipesSerializer(
            instance,
            context={'request': rep_data}
        ).data


class RecipesSerializer(serializers.ModelSerializer):
    """
    Для просмотра полной информации о рецептах.
    """
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientsSerializer(read_only=True, many=True)
    author = UsersSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'tags', 'ingredients',
            'image', 'name',
            'text', 'cooking_time', 'author',
            'is_favorite', 'is_in_shopping_cart'
        )

    def get_is(self, model, user, pk):
        """
        Функция для favorite and shopping_cart.
        """
        if user.is_anonymous:
            return False
        return model.objects.filter(
            user=user, recipe_id=pk
        ).exists()

    def get_is_favorite(self, obj):
        """
        Для проверки избранного.
        """
        request = self.context.get('request')
        return self.get_is(
            user=request.user,
            pk=obj.id,
            model=Favorite
        )

    def get_is_in_shopping_cart(self, obj):
        """
        Для проверки листа покупок.
        """
        request = self.context.get('request')
        return self.get_is(
            model=ShoppingCart,
            user=request.user,
            pk=obj.id
        )


class InfoFollowSerializer(UserSerializer):
    """
    Для вывода информации о подписках.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:CONSTANT]
        return ShortInfoRecipesSerializer(
            recipes,
            many=True
        ).data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        return recipes.count()

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context.get('request').user, author=obj
        ).exists()


class FollowSerializer(UserSerializer):
    """
    Подписки.
    """
    user = serializers.IntegerField(source='user.id')
    author = serializers.IntegerField(source='author.id')

    class Meta:
        model = Follow
        fields = '__all__'

    def validate_following(self, following):
        if self.context.get('request').user == following:
            raise serializers.ValidationError(
                'You cant follow to yourself.'
            )
        return following

    def create(self, validated_data):
        author = validated_data.get("author")
        author = get_object_or_404(User, pk=author.get("id"))
        user = validated_data.get("user")
        return Follow.objects.create(user=user, author=author)

    def to_representation(self, instance):
        return InfoFollowSerializer(
            instance.author,
            context={
                'request': self.context.get('request')
            }
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для избранного.
    """

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def validate_favorite(self, data):
        request = self.context.get('request')
        recipe = Favorite.objects.filter(
            user=request.user, recipe=data['recipe']
        )
        if recipe.exists():
            raise serializers.ValidationError(
                'Already in favorites'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortInfoRecipesSerializer(
            instance.recipe, context=context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для листа поукпок.
    """

    class Meta:
        fields = ['recipe', 'user']
        model = ShoppingCart

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortInfoRecipesSerializer(
            instance.recipe,
            context=context
        ).data
