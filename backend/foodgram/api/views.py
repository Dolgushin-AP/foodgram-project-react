from django.db.models import BooleanField, Exists, OuterRef, Sum, Value
from django.db.transaction import atomic
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from api.filters import NameSearchFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (CartCheckSerializer, FavouriteCheckSerializer, FollowSerializer,
                             IngredientSerializer, MyUserSerializer,
                             RecipeCreateSerializer, RecipeGetSerializer,
                             RecipeShowSerializer, TagSerializer)
# from api.utils import download_cart
from recipes.models import (Favourite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import Follow, User


TO_BUY = 'to_buy_list.txt'


class MyUserViewSet(UserViewSet):
    '''Вьюсет для пользователей и подписок'''

    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    pagination_class = CustomPagination

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if user.id == author.id:
                return Response({'detail': 'Нельзя подписаться на себя!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(author=author, user=user).exists():
                return Response({'detail': 'Вы уже подписаны!'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(author,
                                          context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not Follow.objects.filter(user=user, author=author).exists():
            return Response({'errors': 'Сначала нужно подписаться!'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscription = get_object_or_404(Follow, user=user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Вьюсет ингредиентов'''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (NameSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    '''Вюсет рецептов'''

    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Recipe.objects.annotate(
                is_favorited=Exists(
                    Favourite.objects.filter(
                        user=self.request.user, recipe__pk=OuterRef('pk')
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=self.request.user, recipe__pk=OuterRef('pk')
                    )
                ),
            )
        return Recipe.objects.annotate(
            is_favorited=Value(False, output_field=BooleanField()),
            is_in_shopping_cart=Value(False, output_field=BooleanField()),
        )

    @atomic()
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=['POST'], permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        data = {
            'user': request.user.id,
            'recipe': pk,
        }
        serializer = FavouriteCheckSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        return self.add_method(Favourite, request.user, pk)

    # def favorite(self, request, pk=None):
    #     if request.method == 'POST':
    #         return self.post_method(Favourite, request.user, pk)
    #     return self.delete_method(Favourite, request.user, pk)

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        data = {
            'user': request.user.id,
            'recipe': pk,
        }
        serializer = FavouriteCheckSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        return self.delete_method(Favourite, request.user, pk)

    @action(
        detail=True, methods=['POST'], permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        data = {
            'user': request.user.id,
            'recipe': pk,
        }
        serializer = CartCheckSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        return self.add_method(ShoppingCart, request.user, pk)

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        data = {
            'user': request.user.id,
            'recipe': pk,
        }
        serializer = CartCheckSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        return self.delete_method(ShoppingCart, request.user, pk)

    @atomic()
    def add_method(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShowSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @atomic()
    def delete_method(self, model, user, pk):
        model.objects.filter(user=user, recipe__id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'], detail=False, permission_classes=(IsAuthenticated,)
    )
    def download_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(recipe__list__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .order_by('ingredient__name')
            .annotate(total=Sum('amount'))
        )
        result = 'Ваши покупки'
        result += '\n'.join(
            (
                f'{ingredient["ingredient__name"]} - {ingredient["total"]}/'
                f'{ingredient["ingredient__measurement_unit"]}'
                for ingredient in ingredients
            )
        )
        response = HttpResponse(result, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={TO_BUY}'
        return response

    # queryset = Recipe.objects.all()
    # permission_classes = (IsAuthorOrReadOnly,)
    # pagination_class = CustomPagination
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = RecipeFilter
    # http_method_names = [
    #     m for m in viewsets.ModelViewSet.http_method_names if m not in ['PUT']
    # ]

    # def get_serializer_class(self):
    #     if self.request.method in SAFE_METHODS:
    #         return RecipeGetSerializer
    #     return RecipeCreateSerializer

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)

    # @action(detail=True,
    #         methods=['POST', 'DELETE'],
    #         permission_classes=[IsAuthenticated])
    # def favorite(self, request, pk=None):
    #     if request.method == 'POST':
    #         return self.post_method(Favourite, request.user, pk)
    #     return self.delete_method(Favourite, request.user, pk)

    # @action(detail=True,
    #         methods=['POST', 'DELETE'],
    #         permission_classes=[IsAuthenticated])
    # def shopping_cart(self, request, pk=None):
    #     if request.method == 'POST':
    #         return self.post_method(ShoppingCart, request.user, pk)
    #     return self.delete_method(ShoppingCart, request.user, pk)

    # def post_method(self, model, user, pk):
    #     if model.objects.filter(user=user, recipe__id=pk).exists():
    #         return Response({'errors': 'Рецепт уже в списке'},
    #                         status=status.HTTP_400_BAD_REQUEST)
    #     recipe = get_object_or_404(Recipe, id=pk)
    #     model.objects.create(user=user, recipe=recipe)
    #     serializer = RecipeShowSerializer(recipe)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def delete_method(self, model, user, pk):
    #     obj = model.objects.filter(user=user, recipe__id=pk)
    #     if obj.exists():
    #         obj.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     return Response({'errors': 'Рецепта нет в списке'},
    #                     status=status.HTTP_400_BAD_REQUEST)

    # # @action(detail=False,
    # #         methods=['get'],
    # #         permission_classes=[IsAuthenticated])
    # # def download_cart(self, request):
    # #     return download_cart(self, request)

    # @action(methods=['GET'],
    #         detail=False,
    #         permission_classes=[IsAuthenticated])
    # def download_cart(self, request):
    #     shopping_list = request.user.get_to_buy_list()
    #     response = HttpResponse(shopping_list, 'Content-Type: text/plain')
    #     response['Content-Disposition'] = ('attachment; filename='f'{TO_BUY}')
    #     return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Вьюсет тегов'''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
