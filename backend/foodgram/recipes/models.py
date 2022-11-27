from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tags(models.Model):
    """
    Модель тэгов.
    """
    name = models.CharField(max_length=200, verbose_name='Название тэга')
    color = ColorField(format='hex', verbose_name='hex')
    slug = models.SlugField(unique=True, max_length=200)


class Ingredients(models.Model):
    """
    Модель ингридиентов.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингридиента'
    )
    measure_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measure_unit'],
                name='ingredient_name_unit_unique'
            )
        ]


class Recipes(models.Model):
    """
    Главная модель рецептов.
    """
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredients',
        verbose_name='Ингредиенты',
        related_name='recipes'
    )
    tag = models.ManyToManyField(
        Tags,
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


class RecipeIngredients(models.Model):
    """
    Модель списка ингридиентов.
    """
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    quantity = models.IntegerField(
        default=1,
        validators=[
            MinValueValidator(1, 'Минимальное количество 1')
        ]
    )


class ShoppingCart(models.Model):
    """
    Модель списка покупок.
    """
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    class Meta:
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
        Recipes,
        on_delete=models.CASCADE,
        related_name='in_favorite'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_favorite',
            ),
        )
