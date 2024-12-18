from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, validate_email
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

User = get_user_model()

class StartupProfile(models.Model):
    """
    Represents the profile of a startup on the platform.

    Attributes:
        user (OneToOneField): A one-to-one relationship with the User model.
        company_name (CharField): The name of the startup (max length: 200 characters).
        industry (CharField): The industry category of the startup (max length: 100 characters).
        size (CharField): The size of the startup (e.g., small, medium, large).
        country (CharField): The country where the startup is located (max length: 50 characters).
        city (CharField): The city where the startup is located (max length: 50 characters).
        zip_code (CharField): The postal code of the startup (max length: 20 characters).
        address (CharField): The physical address of the startup (max length: 250 characters, optional).
        phone (PhoneNumberField): The startup's phone number in international format (optional).
        email (EmailField): The unique email address of the startup.
        description (TextField): A detailed description of the startup (max length: 1000 characters, optional).
        created_at (DateTimeField): The date and time the profile was created.
        updated_at (DateTimeField): The date and time the profile was last updated.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="startup_profile", db_index=True)
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    address = models.CharField(max_length=250, blank=True, null=True)
    phone = PhoneNumberField(null=True, blank=True)
    email = models.EmailField(unique=True, db_index=True, validators=[validate_email])
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
    """
    Represents the profile of an investor on the platform.

    Attributes:
        user (OneToOneField): A one-to-one relationship with the User model.
        country (CharField): The country of the investor (max length: 50 characters).
        city (CharField): The city of the investor (max length: 50 characters).
        zip_code (CharField): The postal code of the investor (max length: 20 characters).
        address (CharField): The physical address of the investor (max length: 250 characters, optional).
        phone (PhoneNumberField): The investor's phone number in international format (optional).
        email (EmailField): The unique email address of the investor.
        account_balance (DecimalField): The balance in the investor's account, 
                                        with a default value of 0.00 and a minimum value of 0.00.
        created_at (DateTimeField): The date and time the profile was created.
        updated_at (DateTimeField): The date and time the profile was last updated.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="investor_profile", db_index=True)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    address = models.CharField(max_length=250, blank=True, null=True)
    phone = PhoneNumberField(null=True, blank=True)
    email = models.EmailField(unique=True, db_index=True, validators=[validate_email])
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