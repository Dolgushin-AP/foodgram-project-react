from django_filters.rest_framework import (
    filters,
    FilterSet,
    ModelMultipleChoiceFilter
)
# from django.contrib.auth import get_user_model
# from django.core.exceptions import ValidationError
# from django.forms.fields import MultipleChoiceField
# from django_filters.rest_framework import FilterSet, filters
# from django_filters.widgets import BooleanWidget
# from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


# User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favoure = filters.BooleanFilter(method='filter_is_favoure')
    is_in_cart = filters.BooleanFilter(method='filter_is_in_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_is_favoure(self, queryset, field_name, value):
        current_user = self.request.user
        if value and current_user.is_authenticated:
            lookup = field_name
            return queryset.filter(**{lookup: current_user})
        return queryset

    def filter_is_in_cart(self, queryset, field_name, value):
        current_user = self.request.user
        if value and current_user.is_authenticated:
            lookup = field_name
            return queryset.filter(**{lookup: current_user})
        return queryset


# class NameSearchFilter(SearchFilter):
#     search_param = 'name'


# class TagMultipleChoiceField(MultipleChoiceField):
#     '''Фильтрация по тэгам'''

#     def validate(self, value):
#         if self.required and not value:
#             raise ValidationError(
#                 self.error_messages['required'], code='required'
#             )
#         for val in value:
#             if val in self.choices and not self.valid_value(val):
#                 raise ValidationError(
#                     self.error_messages['invalid_choice'],
#                     code='invalid_choice',
#                     params={'value': val},
#                 )


# class TagFilter(filters.AllValuesMultipleFilter):

#     field_class = TagMultipleChoiceField


# class RecipeFilter(FilterSet):
#     '''Фильтрация рецептов'''

#     author = filters.AllValuesMultipleFilter(
#         field_name='author__id', label='автор'
#     )
#     is_in_cart = filters.BooleanFilter(
#         widget=BooleanWidget(), label='В корзине.'
#     )
#     is_favoure = filters.BooleanFilter(
#         widget=BooleanWidget(), label='В избранном.'
#     )
#     tags = TagFilter(field_name='tags__slug')

#     class Meta:
#         model = Recipe
#         fields = ('author', 'tags', 'is_in_cart', 'is_favoure')


# class RecipeFilter(rest_framework.FilterSet):
#     author = rest_framework.ModelChoiceFilter(queryset=User.objects.all())
#     tags = rest_framework.AllValuesMultipleFilter(field_name='tags__slug')
#     is_favoure = rest_framework.BooleanFilter(method='filter_is_favoure')
#     is_in_cart = rest_framework.BooleanFilter(
#         method='filter_is_in_cart')

#     class Meta:
#         model = Recipe
#         fields = ('author', 'tags', 'is_favoure', 'is_in_cart')

#     def filter_is_favoure(self, queryset, name, value):
#         if value and self.request.user.is_authenticated:
#             return queryset.filter(favourites__user=self.request.user)
#         return queryset

#     def filter_is_in_cart(self, queryset, name, value):
#         if value and self.request.user.is_authenticated:
#             return queryset.filter(shopping__user=self.request.user)
#         return queryset
