from django.contrib.auth import get_user_model
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from communications.models import Room, Message
from users.models import *
from datetime import datetime

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        if not self.scope["user"].is_authenticated:
            await self.close(code=403)
            return

        room_exists = await sync_to_async(
            Room.objects.filter(name=self.room_name).first
        )()
        if not room_exists:
            await self.close(code=404)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message")

            if not message:
                await self.send(json.dumps({"error": "Empty message is not allowed."}))
                return

            sender = str(self.scope["user"].get_full_name())

            room = await sync_to_async(Room.objects.filter(name=self.room_name).first)()
            if room:
                new_message = Message(
                    user=self.scope["user"].user_id,
                    content=message,
                    timestamp=datetime.utcnow(),
                )
                if not hasattr(room, "messages"):
                    room.messages = []
                room.messages.append(new_message)
                await sync_to_async(room.save)()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": sender,
                },
            )
        except json.JSONDecodeError:
            await self.send(json.dumps({"error": "Invalid JSON format received."}))
        except Exception as e:
            import logging

            logging.error(f"Error in receive: {str(e)}")
            await self.send(json.dumps({"error": f"Unexpected error: {str(e)}"}))

    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]

        await self.send(
            json.dumps({"type": "chat_message", "message": message, "sender": sender})
        )
