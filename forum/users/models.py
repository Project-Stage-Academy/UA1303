from django.db import models

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import datetime
import re

ROLE_CHOICES = [
    (0, "Unassigned"),
    (1, "Startup"),
    (2, "Investor"),
]


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if email:
            email_pattern = r"^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z0-9]+$"
            if not re.match(email_pattern, email):
                raise ValueError("The Email is not valid")
        else:
            raise ValueError("The Email field must be set")
        if password:
            password_pattern = r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z]).{8,}$"
            if not re.match(password_pattern, password):
                raise ValueError("Password is not matching valid pattern")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    user_phone = models.CharField(max_length=30)
    title = models.CharField(max_length=30)
    role = models.IntegerField(choices=ROLE_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True,editable=False)
    last_login = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "users"
        ordering = ["user_id"]

    def __str__(self):
        return f"id:{self.user_id} - {self.first_name} - {self.last_name}"
