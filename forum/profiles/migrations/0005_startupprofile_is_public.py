# Generated by Django 5.1.4 on 2025-01-02 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_investorprofile_followed_startups'),
    ]

    operations = [
        migrations.AddField(
            model_name='startupprofile',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
    ]
