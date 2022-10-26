from colorfield.filds import ColorField
from django.db import models

class Tags(models.Model):
    """
    Модель тэгов.
    """
    name = models.CharField(max_length=200)
    color = ColorField(default='#FF0000')
    #slug =
    pass


class Ingredients(models.Model):
    """
    Модель ингридиентов.
    """
    name = models.CharField(
        max_length=200
    )
    measure_unit = models.CharField(
        max_length=200
    )


class Recipes(models.Model):
    """
    Главная модель рецептов.
    """
    #ingredients = models.ForeignKey(
#        Ingredients,
#       on_delete=models.CASCADE,
#       related_name='recipes'
    )
    tags = models.ForeignKey(
        Tags,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    #pub_date=
    #image=
    #name = models.CharField(max_length=200)
    #text=
    #cooking_time=
    #author=


class RecipeIngredients(models.Model):
    """
    Модель списка ингридиентов.
    """
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    recipe= models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    quantity = models.IntegerField()