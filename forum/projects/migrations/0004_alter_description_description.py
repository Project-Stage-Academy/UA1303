# Generated by Django 4.1 on 2024-12-23 21:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
        ('projects', '0003_add_descriptions')
    ]

    operations = [
        migrations.AlterField(
            model_name='description',
            name='description',
            field=models.TextField(blank=True, validators=[django.core.validators.MaxLengthValidator(2000)]),
        ),
    ]