from mongoengine import Document, fields, EmbeddedDocument
from datetime import datetime


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
    messages = fields.ListField(
        fields.EmbeddedDocumentField(Message), default=list
    )  
