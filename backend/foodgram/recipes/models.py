from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """
    Модель тэгов.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название тэга'
    )
    color = ColorField(
        format='hex',
        verbose_name='hex'
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """
    Модель ингридиентов.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Главная модель рецептов.
    """
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    pub_date = models.DateField('Дата публикации', auto_now_add=True)
    image = models.ImageField(
        upload_to='recipes/images',
        verbose_name='Картинка'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    text = models.CharField(
        max_length=500,
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1, 'Минимальное время 1 минута')
        ]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Модель списка ингридиентов.
    """
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиенты рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    amount = models.IntegerField(
        default=1,
        validators=[
            MinValueValidator(1, 'Минимальное количество 1')
        ],
        verbose_name='Количество ингредиентов'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "ingredients",
                    "recipe",
                ),
                name="unique_ingredients_recipe",
            ),
        )

    def __str__(self):
        return f'{self.recipe}: {self.ingredients} – {self.amount}'


class ShoppingCart(models.Model):
    """
    Модель списка покупок.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Корзина рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_shopping_cart',
            ),
        )


class Favorite(models.Model):
    """
    Модель отслеживания рецептов.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorite'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_favorite',
            ),
        )
