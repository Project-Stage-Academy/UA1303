from mongoengine import Document, fields, EmbeddedDocument
from datetime import datetime
from django.contrib.auth.hashers import make_password


class Message(EmbeddedDocument):
    user = fields.IntField()
    content = fields.StringField(max_length=512, required=True)
    timestamp = fields.DateTimeField(default=datetime.utcnow)

    def clean(self):
        if len(self.content) > 512:
            raise fields.ValidationError("Content must have less than 512 characters.")


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


# from mongoengine import Document, IntField, StringField, SequenceField


# class Counter(Document):
#     name = StringField(
#         required=True, unique=True
#     )  # Назва лічильника (наприклад, "user_id")
#     value = IntField(default=0)  # Поточне значення лічильника


# def get_next_sequence_value(sequence_name):
#     counter = Counter.objects(name=sequence_name).modify(
#         upsert=True,  # Створити новий документ, якщо він не існує
#         new=True,  # Повернути оновлений документ
#         inc__value=1,  # Збільшити значення на 1
#     )
#     return counter.value


# class User(Document):
#     user_id = fields.IntField(unique=True)
#     email = fields.StringField(required=True)
#     password = fields.StringField(required=True)

#     def save(self, *args, **kwargs):
#         if not self.user_id:  # Якщо user_id не встановлено
#             self.user_id = get_next_sequence_value(
#                 "user_id"
#             )  # Отримати наступне значення
#         super(User, self).save(*args, **kwargs)

#     def set_password(self, raw_password):
#         self.password = make_password(raw_password)
#         self.save()
