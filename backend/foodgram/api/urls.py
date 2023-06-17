from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, MyUserViewSet, RecipeViewSet,
                       TagViewSet)


app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('users', MyUserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
