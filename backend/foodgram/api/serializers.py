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

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj.id).exists()


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
        fields = [
            'id', 'name',
            'measurement_unit', 'amount'
        ]


class ShortInfoRecipesSerializer(serializers.ModelSerializer):
    """
    Вывод краткой информации о рецепте
    """
    tags = TagSerializer(read_only=True, many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'name', 'image', 'cooking_time')


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
        ingredients_data = validated_data.pop('ingredients')
        if not ingredients_data:
            raise ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        unique_ingredients = set()
        for ingredient in ingredients_data:
            if ingredient.get('amount') <= 0:
                raise ValidationError(
                    'Количество ингредиентов должно быть больше нуля'
                )
            if ingredient['id'] in unique_ingredients:
                raise ValidationError(
                    'Ингредиенты в рецепте не должны повторяться'
                )
            unique_ingredients.add(ingredient['id'])

        request = self.context.get('request')
        tag_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=request.user
        )
        recipe.tags.set(tag_data)
        self.create_ingredients(ingredients=ingredients_data, recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop("ingredients")
        unique_ingredients = set()

        for ingredient in ingredients:
            if ingredient.get('amount') <= 0:
                raise ValidationError(
                    'Количество ингредиентов должно быть больше нуля'
                )
            if ingredient['id'] in unique_ingredients:
                raise ValidationError(
                    'Ингредиенты в рецепте не должны повторяться'
                )
            unique_ingredients.add(ingredient['id'])
        instance.tags.clear()
        instance.ingredients.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.tags.set(tags)
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

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
    id = serializers.IntegerField()
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientInRecipesSerializer(
        many=True, source='recipe_ingredients'
    )
    author = UsersSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients',
            'image', 'name',
            'text', 'cooking_time', 'author',
            'is_favorited', 'is_in_shopping_cart'
        )

    @staticmethod
    def get_is(model, user, obj):
        """
        Функция для favorite and shopping_cart.
        """
        if user.is_anonymous:
            return False
        return model.objects.filter(
            recipe=obj
        ).exists()

    def get_is_favorited(self, obj):
        """
        Для проверки избранного.
        """
        request = self.context.get('request')
        return self.get_is(
            user=request.user,
            obj=obj,
            model=Favorite
        )

    def get_is_in_shopping_cart(self, obj):
        """
        Для проверки листа покупок.
        """
        request = self.context.get('request')
        return self.get_is(
            user=request.user,
            obj=obj,
            model=ShoppingCart
        )


class FollowSerializer(UsersSerializer):
    """Сериализатор для добавления/удаления подписки, просмотра подписок."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UsersSerializer.Meta):
        fields = UsersSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, object):
        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = request.query_params.get('recipe_limit')
        queryset = object.recipes.all()
        if recipe_limit:
            queryset = queryset[:int(recipe_limit)]
        return ShortInfoRecipesSerializer(
            queryset, context=context, many=True
        ).data

    def get_recipes_count(self, object):
        return object.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для избранного.
    """

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def validate(self, data):
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'error': 'Этот рецепт уже добавлен'}
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
        model = ShoppingCart
        fields = ('recipe', 'user')

    def validate(self, data):
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'error': 'Этот рецепт уже добавлен'}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortInfoRecipesSerializer(
            instance.recipe, context=context
        ).data
