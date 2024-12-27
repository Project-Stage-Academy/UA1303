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
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def get_users_id(self):
        return {
            "user_1": int(self.name.split("_")[1:][0]),
            "user_2": int(self.name.split("_")[1:][1]),
        }

    def get_users_names(self):
        User = get_user_model()
        return {
            "user_1": User.objects.get(
                user_id=self.get_users_id()["user_1"]
            ).first_name,
            "user_2": User.objects.get(
                user_id=self.get_users_id()["user_2"]
            ).first_name,
        }

    def __str__(self):
        return f"{self.name} ({self.get_online_count()})"


class Message(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    content = encrypt(models.CharField(max_length=512))
    timestamp = models.DateTimeField(auto_now_add=True)
