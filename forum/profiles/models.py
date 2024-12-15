from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

# Create your models here.

class StartupProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="startup_profile")
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InvestorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="investor_profile")
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    account_balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        validators=[MinValueValidator(0.00)]
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)