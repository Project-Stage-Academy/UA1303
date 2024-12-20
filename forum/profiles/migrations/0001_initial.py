# Generated by Django 4.1 on 2024-12-19 20:50

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StartupProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200)),
                ('industry', models.CharField(max_length=100)),
                ('size', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=20)),
                ('address', models.CharField(blank=True, max_length=250, null=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True, validators=[django.core.validators.EmailValidator()])),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='startup_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Startup Profile',
                'verbose_name_plural': 'Startup Profiles',
                'db_table': 'startup_profiles',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='InvestorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=20)),
                ('address', models.CharField(blank=True, max_length=250, null=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True, validators=[django.core.validators.EmailValidator()])),
                ('account_balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=15, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='investor_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Investor Profile',
                'verbose_name_plural': 'Investor Profiles',
                'db_table': 'investor_profiles',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='investorprofile',
            constraint=models.CheckConstraint(check=models.Q(('account_balance__gte', 0)), name='account_balance_non_negative'),
        ),
    ]
