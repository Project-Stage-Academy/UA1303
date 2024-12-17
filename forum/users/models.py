from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from phonenumber_field.modelfields import PhoneNumberField

ROLE_CHOICES = [
    (0, "Unassigned"),
    (1, "Startup"),
    (2, "Investor"),
    (3, "Both")
]


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True, db_index=True)
    user_phone = PhoneNumberField(null=True, blank=True)
    title = models.CharField(max_length=30, null=True, blank=True)
    role = models.IntegerField(choices=ROLE_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)  
    is_active = models.BooleanField(default=True)  
    is_superuser = models.BooleanField(default=False)  

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "users"
        ordering = ["user_id"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"id:{self.user_id} - {self.first_name} {self.last_name} (Role: {self.get_role_display()})"
