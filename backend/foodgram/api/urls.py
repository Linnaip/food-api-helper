from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientsViewSet, RecipesViewSet, UserViewSet


router = DefaultRouter()

router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls))
]
# USERS
# /api/users/ GET, POST
# /api/users/{id}/ GET
# /api/users/me/ GET
# /api/users/set_password/ POST
# /api/auth/token/login/ POST
# /api/auth/token/logout POST
# SUBSCRIPT
# /api/users/subscriptions/ GET
# /api/users/id/subscribe/ POST, DELETE
# Recipes
# /api/recipes/ GET, POST
# /api/recipes/id/ GET, PATCH, DELETE
# Download_shopping_cart
# /api/recipes/download_shopping_cart/ GET
# /api/recipes/id/shopping_cart/ POST, DELETE
# FAVORITE
# /api/recipes/id/favorite/ POST, DELETE

# Работает:

# TAGS
# /api/tags/ GET
# /api/tags/id/ GET

# INGREDIENTS
# /api/ingredients/ GET
# /api/ingredients/id/ GET
