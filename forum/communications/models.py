from mongoengine import Document, fields, EmbeddedDocument
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(EmbeddedDocument):
    user = fields.IntField()
    content = fields.StringField(max_length=512, required=True)
    timestamp = fields.DateTimeField(default=datetime.utcnow)

    def clean(self):
        if len(self.content) > 512:
            raise fields.ValidationError("Content must have less than 512 characters.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Room(Document):
    name = fields.StringField(max_length=128, required=True)
    participants = fields.ListField(fields.IntField(), required=True)
    messages = fields.ListField(fields.EmbeddedDocumentField(Message), default=list)

    def join(self, user):
        if user.user_id not in self.participants:
            self.participants.append(user.user_id)
            self.save()

    def leave(self, user):
        if user.user_id in self.participants:
            self.participants.remove(user.user_id)
            self.save()

    def get_users_names(self):
        participant_1 = User.objects.filter(pk=self.participants[0]).first()
        participant_2 = User.objects.filter(pk=self.participants[1]).first()

        return {
            f"user_{self.participants[0]}": participant_1.first_name,
            f"user_{self.participants[1]}": participant_2.first_name,
        }

    def get_online_count(self):
        return len(self.participants)
