import base64
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
from users.models import Follow, User


class MyUserSerializer(UserSerializer):
    '''Сериализатор пользователя'''

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class FollowSerializer(MyUserSerializer):
    '''Сериализатор подписoк'''

    recipes_count = serializers.IntegerField(source='recipes.count',
                                             read_only=True)
    recipes = SerializerMethodField(method_name='get_recipes')
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'recipes_count', 'recipes',
                  'is_subscribed')
        read_only_fields = ('email', 'username',
                            'first_name', 'last_name')

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        serializer = RecipeShowSerializer(recipes, many=True,
                                           context=self.context)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор тегов'''

    class Meta:
        model = Tag
        fields = ('id', 'name', 'colour', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор ингридиентов'''

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeCreationSerializer(ModelSerializer):
    '''Сериализатор для вывода ингредиента при создании рецепта'''

    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.ingredient.id
        return data


class Base64ImageField(serializers.ImageField):
    """Кастомный сериализатор поля для фото рецепта"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeGetSerializer(ModelSerializer):
    '''Сериализатор получения рецепта'''

    tags = TagSerializer(many=True, read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientRecipeCreationSerializer(
        source='recipeingredients', many=True)
    image = Base64ImageField()
    is_favoure = SerializerMethodField(read_only=True)
    is_in_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favoure', 'is_in_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favoure(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favourite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeCreateSerializer(ModelSerializer):
    '''Сериализатор создания рецепта'''

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientRecipeCreationSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate_tags(self, value):
        if not value:
            raise ValidationError('Добавьте тег.')
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Добавьте ингридиент.')
        for i in value:
            if i['amount'] <= 0:
                raise ValidationError('Количество должно быть больше нуля!')
        return value

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeGetSerializer(instance,
                                   context=context).data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredients.objects.create(recipe=recipe,
                                             ingredient=ingredient.get('id'),
                                             amount=ingredient.get('amount'))
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
            for ingredient in ingredients:
                amount = ingredient['amount']
                RecipeIngredients.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient.get('id'),
                    defaults={'amount': amount})
        return super().update(instance, validated_data)


class RecipeShowSerializer(ModelSerializer):
    '''
    Дополнительный сериализатор для отображения рецептов
    в подписках, избранном и покупках
    '''

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
