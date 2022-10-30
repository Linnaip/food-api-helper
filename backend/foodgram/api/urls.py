from django.contrib import admin
from django.urls import path

urlpatterns = [

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
# TAGS
# /api/tags/ GET
# /api/tags/id/ GET
# Recipes
# /api/recipes/ GET, POST
# /api/recipes/id/ GET, PATCH, DELETE
# Download_shopping_cart
# /api/recipes/download_shopping_cart/ GET
# /api/recipes/id/shopping_cart/ POST, DELETE
# FAVORITE
# /api/recipes/id/favorite/ POST, DELETE
# INGREDIENTS
# /api/ingredients/ GET
# /api/ingredients/id/ GET
