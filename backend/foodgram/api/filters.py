from django.contrib.auth import get_user_model
from django_filters import rest_framework
from rest_framework.filters import SearchFilter
from recipes.models import Recipe
User = get_user_model()


class NameSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.ModelChoiceFilter(queryset=User.objects.all())
    tags = rest_framework.AllValuesMultipleFilter(field_name='tags__slug')
    is_favoure = rest_framework.BooleanFilter(method='filter_is_favoure')
    is_in_cart = rest_framework.BooleanFilter(
        method='filter_is_in_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favoure', 'is_in_cart')

    def filter_is_favoure(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favourites__user=self.request.user)
        return queryset
    
    def filter_is_in_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping__user=self.request.user)
        return queryset