from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers


from recipes.models import Tags, Ingredients, Recipes, Favorite, ShoppingCart, RecipeIngredients
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

    def get_is_subscribed(self, obj: User):
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
    """
    Сериализатор для вывода ингредиентов.
    """
    class Meta:
        model = Ingredients
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
        model = RecipeIngredients
        fields = (
            'id', 'name',
            'measurement_unit', 'quantity',
        )


class ShortInfoRecipesSerializer(serializers.ModelSerializer):
    """
    Вывод краткой информации о рецепте
    """
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class CreateIngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Для создания ингредиетов.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'quantity',
        )

    def create(self, validated_data):
        create = RecipeIngredients.objects.create(
            ingredients=validated_data.get('id'),
            quantity=validated_data.get('quantity')
        )
        return create


class CreateRecipesSerializer(serializers.ModelSerializer):
    """
    Для создания рецептов.
    """
    image = Base64ImageField(use_url=True, max_length=None)
    tag = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all()
    )
    ingredients = CreateIngredientRecipeSerializer(many=True)
    author = UsersSerializer(read_only=True)
    name = serializers.CharField(max_length=200)

    class Meta:
        model = Recipes
        fields = (
            'id', 'author', 'tag',
            'image', 'name', 'text',
            'cooking_time', 'ingredients'
        )

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                quantity=ingredient.get('quantity'),
            )

    def create(self, validated_data):
        author_data = self.context.get('request').user
        ingredients_data = validated_data.pop('ingredients')
        tag_data = validated_data.pop('tag')
        image_data = validated_data.pop('image')
        recipe = Recipes.objects.create(
            **validated_data,
            image=image_data,
            author=author_data
        )
        recipe.tag.set(tag_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def to_representation(self, instance):
        rep_data = self.context.get('request')
        result = RecipesSerializer(instance,
                                   context={'request': rep_data}).data
        return result


class RecipesSerializer(serializers.ModelSerializer):
    """
    Для просмотра полной информации о рецептах.
    """
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
        """
        Для проверки избранного.
        """
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Для проверки листа покупок.
        """
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


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для избранного.
    """
    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def validate_favorite(self, data):
        request = self.context.get('request')
        recipe = Favorite.objects.filter(user=request.user, recipe=data['recipe'])
        if recipe.exists():
            raise serializers.ValidationError(
                'Already in favorites'
            )
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для листа поукпок.
    """
    class Meta:
        fields = ['recipe', 'user']
        model = ShoppingCart

    def to_representation(self, instance):
        request=self.context.get('request')
        context = {'request': request}
        result = RecipesSerializer(instance.recipe, context=context).data
        return result
