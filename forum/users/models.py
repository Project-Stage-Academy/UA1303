from __future__ import annotations
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from phonenumber_field.modelfields import PhoneNumberField
from enum import IntEnum


class Role(IntEnum):
    UNASSIGNED = 0
    STARTUP = 1
    INVESTOR = 2
    BOTH = 3

    @classmethod
    def has_role(cls, user_role: int, role: Role) -> bool:
        '''
        Checks if user role alligns to specific role.
        It relies on current role list - `[UNASSIGNED, STARTUP, INVESTOR, BOTH]`,
        and always returns `True` if user model `role` field is `BOTH`,
        so it is important to make sure to adjust logic if roles change.
        '''
        return user_role == role or user_role == Role.BOTH

    @classmethod
    def token_role_aligns(cls, token_role: int, required_role: Role):
        '''
        Check whether token role alligns to required one.
        '''
        return token_role == required_role.value


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
    ROLE_CHOICES = [(role.value, role.name.capitalize()) for role in Role]
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

    groups = models.ManyToManyField(
        "auth.Group", related_name="customuser_groups", blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="customuser_permissions", blank=True
    )

    class Meta:
        db_table = "users"
        ordering = ["user_id"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"id:{self.user_id} - {self.first_name} {self.last_name} (Role: {self.get_role_display()})"
