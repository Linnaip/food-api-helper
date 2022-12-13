from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
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
            'measurement_unit', 'quantity',
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
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredients'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'quantity',
        )

    def create(self, validated_data):
        return RecipeIngredient.objects.create(
            ingredients=validated_data.get('id'),
            quantity=validated_data.get('quantity')
        )


class CreateRecipesSerializer(serializers.ModelSerializer):
    """
    Для создания рецептов.
    """
    image = Base64ImageField(use_url=True, max_length=None)
    tag = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = CreateIngredientRecipeSerializer(many=True)
    author = UsersSerializer(read_only=True)
    name = serializers.CharField(max_length=200)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'tag',
            'image', 'name', 'text',
            'cooking_time', 'ingredients'
        )

    def validate(self, data):
        ing_list = []
        for ingredient in data['ingredients']:
            if ingredient['id'] in ing_list:
                if len(ing_list) != len(set(ing_list)):
                    raise ValidationError(
                        'Ингредиенты повторяются.'
                    )
            ing_list.append(ing_list)
        return data

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bult_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                quantity=ingredient.get('quantity'),
            ) for ingredient in ingredients
        )

    def create(self, validated_data):
        author_data = self.context.get('request').user
        ingredients_data = validated_data.pop('ingredients')
        tag_data = validated_data.pop('tag')
        image_data = validated_data.pop('image')
        recipe = Recipe.objects.create(
            **validated_data,
            image=image_data,
            author=author_data
        )
        recipe.tag.set(tag_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tag")
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
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
    tag = TagSerializer(read_only=True, many=True)
    ingredients = IngredientsSerializer(read_only=True, many=True,
                                        source='ingredients_recipe')
    author = UsersSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tag',
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

    def get_is_favorite(self, request, obj):
        """
        Для проверки избранного.
        """
        return self.get_is(
            user=request.user,
            pk=obj.id,
            model=Favorite
        )

    def get_is_in_shopping_cart(self, request, obj):
        """
        Для проверки листа покупок.
        """
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
