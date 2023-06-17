# Generated by Django 4.2.1 on 2023-06-17 10:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='colour',
        ),
        migrations.AddField(
            model_name='tag',
            name='color',
            field=models.CharField(default=1, max_length=7, unique=True, verbose_name='Цвет HEX-код'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Минимальное значение - 1!')], verbose_name='Время приготовления, мин'),
        ),
    ]
