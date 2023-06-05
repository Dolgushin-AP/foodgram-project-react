from datetime import datetime

from django.core.exceptions import ValidationError


def validate_ingredients(self, value):
    '''Валидатор ингредиентов'''
    if not value:
        raise ValidationError('Добавьте ингредиент.')
    for ingredient in value:
        if ingredient['amount'] <= 0:
            raise ValidationError('Количество должно быть больше нуля!')
    return value

def validate_username(value):
    '''Валидатор имени пользователя'''
    if value.lower() == 'me':
        raise ValidationError(
            ('Недопустимое имя пользователя.'),
            params={'value': value},
        )

def validate_year(value):
    '''Валидатор даты'''
    year = datetime.now().year
    if not (value <= year):
        raise ValidationError('Дата указана не корректно!')
    return value
