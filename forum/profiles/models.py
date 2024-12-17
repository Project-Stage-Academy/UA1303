from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class StartupProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="startup_profile", db_index=True)
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    address = models.CharField(max_length=250, blank=True, null=True)
    phone = PhoneNumberField(null=True, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "startup_profiles"
        verbose_name = "Startup Profile"
        verbose_name_plural = "Startup Profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"StartupProfile("
            f"id={self.pk}, "
            f"user={self.user.first_name} {self.user.last_name}, "
            f"company={self.company_name}, "
            f"email={self.email}"
            f")"
        )

class InvestorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="investor_profile", db_index=True)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    address = models.CharField(max_length=250, blank=True, null=True)
    phone = PhoneNumberField(null=True, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    account_balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        validators=[MinValueValidator(0.00)]
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "investor_profiles"
        verbose_name = "Investor Profile"
        verbose_name_plural = "Investor Profiles"
        ordering = ["-created_at"]
        constraints = [models.CheckConstraint(check=models.Q(account_balance__gte=0), name='account_balance_non_negative')]

    def __str__(self):
        return (
            f"InvestorProfile("
            f"id={self.pk}, "
            f"user={self.user.first_name} {self.user.last_name}, "
            f"email={self.email}"
            f")"
        )