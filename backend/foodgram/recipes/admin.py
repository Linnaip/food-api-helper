from django.contrib import admin

from .models import Tags, Ingredients, RecipeIngredients, Recipes


class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measure_unit')


class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('ingredients', 'recipe', 'quantity')


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author'
    )


admin.site.register(Tags, TagsAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(RecipeIngredients, RecipeIngredientsAdmin)
admin.site.register(Recipes, RecipeAdmin)
