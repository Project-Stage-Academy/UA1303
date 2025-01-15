from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from forum.profiles.models import StartupProfile
from forum.users.models import Role

# Create your models here.

User = get_user_model()


class ViewedStratups(models.Model):
    """
    Model to track startup views by investors.

    Fields:
        user (ForeignKey): Reference to the user model. The user must have the role "Investor" or "Both".
        startup (ForeignKey): Reference to the StartupProfile model representing the viewed startup.
        viewed_at (DateTimeField): The timestamp when the startup was viewed.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'startup'], name='unique_user_startup_view')
        ]
        ordering = ["-viewed_at"]

    def clean(self):
        """
        Additional validation before saving:
        - Ensures that the user has the role "Investor" or "Both".
        """
        if not Role.has_role(self.user.role, Role.INVESTOR):
            raise ValidationError('The user must have the role "Investor" or "Both".')
        
    def __str__(self):
        return f"{self.user} viewed {self.startup} {self.viewed_at}"
    