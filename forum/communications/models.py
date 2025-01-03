import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django_cryptography.fields import encrypt
import mongoengine as me
from datetime import datetime

User = get_user_model()


# class Room(models.Model):
#     name = models.CharField(max_length=128)
#     online = models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)

#     def get_online_count(self):
#         return self.online.count()

#     def join(self, user):
#         self.online.add(user)

#     def leave(self, user):
#         self.online.remove(user)

#     def get_users_id(self):
#         return {
#             "user_1": int(self.name.split("_")[1:][0]),
#             "user_2": int(self.name.split("_")[1:][1]),
#         }

#     def get_users_names(self):
#         return {
#             "user_1": self.online.first().first_name if self.online.exists() else None,
#             "user_2": (
#                 self.online.last().first_name if self.online.count() > 1 else None
#             ),
#         }

#     def __str__(self):
#         return f"{self.name} ({self.get_online_count()})"


# class Message(models.Model):
#     user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
#     content = encrypt(models.CharField(max_length=512))
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
#         if len(self.content) > 512:
#             raise ValueError("Content must have less than 512 characters.")
#         super().save(*args, **kwargs)


class Room(me.Document):
    name = me.StringField(max_length=128, required=True)
    online = me.ListField(me.ReferenceField("User"))
    created_at = me.DateTimeField(auto_now_add=True)

    def get_online_count(self):
        return len(self.online)

    def join(self, user):
        if user not in self.online:
            self.online.append(user)
            self.save()

    def leave(self, user):
        if user in self.online:
            self.online.remove(user)
            self.save()

    def get_users_id(self):
        user_ids = self.name.split("_")[1:]
        return {"user_1": int(user_ids[0]), "user_2": int(user_ids[1])}

    def __str__(self):
        return f"{self.name} ({self.get_online_count()})"


class Message(me.Document):
    user = me.ReferenceField("User", required=True)
    room = me.ReferenceField(Room, required=True)
    content = me.StringField(max_length=512, required=True)
    timestamp = me.DateTimeField(default=datetime.utcnow)

    def clean(self):
        if len(self.content) > 512:
            raise me.ValidationError("Content must have less than 512 characters.")


