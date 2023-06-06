from django.utils import timezone

from django.core.exceptions import ValidationError


def validate_username(value):
    '''Валидатор имени пользователя'''
    if value.lower() == 'me':
        raise ValidationError(
            ('Недопустимое имя пользователя.'),
            params={'value': value},
        )

def validate_year(value):
    '''Валидатор даты'''
    year = timezone.now().year
    if not (value <= year):
        raise ValidationError('Дата указана не корректно!')
    return value
