from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django_cryptography.fields import encrypt

User = get_user_model()


class Room(models.Model):
    name = models.CharField(max_length=128)
    online = models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)

    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)

    def leave(self, user):
        self.online.remove(user)

    def get_users_id(self):
        return {
            "user_1": int(self.name.split("_")[1:][0]),
            "user_2": int(self.name.split("_")[1:][1]),
        }

    def get_users_names(self):
        return {
            "user_1": self.online.first().first_name if self.online.exists() else None,
            "user_2": (
                self.online.last().first_name if self.online.count() > 1 else None
            ),
        }

    def __str__(self):
        return f"{self.name} ({self.get_online_count()})"


class Message(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    content = encrypt(models.CharField(max_length=512))
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if len(self.content) > 512:
            raise ValueError("Content must have less than 512 characters.")
        super().save(*args, **kwargs)
