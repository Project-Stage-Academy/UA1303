from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status

from channels.testing import WebsocketCommunicator

from .consumers import ChatConsumer
from .models import Room, Message


User = get_user_model()


class RoomModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="password"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="password"
        )
        self.room = Room.objects.create(name="room_1_2")

    def test_room_name(self):
        self.assertEqual(self.room.name, "room_1_2")

    def test_join_user(self):
        self.room.join(self.user1)
        self.assertIn(self.user1, self.room.online.all())

    def test_leave_user(self):
        self.room.join(self.user1)
        self.room.leave(self.user1)
        self.assertNotIn(self.user1, self.room.online.all())

    def test_get_users_id(self):
        self.assertEqual(self.room.get_users_id(), {"user_1": 1, "user_2": 2})

    def test_get_users_names(self):

        self.room.name = f"room_{self.user1.user_id}_{self.user2.user_id}"
        self.room.save()
        self.room.online.set([self.user1, self.user2])

        expected_names = {
            "user_1": self.user1.first_name,
            "user_2": self.user2.first_name,
        }
        self.assertEqual(self.room.get_users_names(), expected_names)

    def test_leave_nonexistent_user(self):
        self.room.leave(self.user1)
        self.assertNotIn(self.user1, self.room.online.all())

    def test_get_online_count_empty_room(self):
        self.assertEqual(self.room.get_online_count(), 0)

    def test_message_encryption(self):
        room = Room.objects.create(name="room_1_2")
        message = Message.objects.create(user=self.user1, room=room, content="Hello!")
        self.assertEqual(message.content, "Hello!")

    def test_message_max_length(self):
        room = Room.objects.create(name="room_1_2")
        long_message = "x" * 513
        with self.assertRaises(ValueError):
            Message.objects.create(user=self.user1, room=room, content=long_message)


class ChatConsumerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="chat_user@example.com",
            first_name="John",
            last_name="Doe",
            password="password",
            is_active=True,
        )
        self.room = Room.objects.create(name="chat_2_1")

    async def connect_to_chat(self, user):
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/api/v1/communications/room/chat_2_1/"
        )
        communicator.scope["user"] = user
        communicator.scope["url_route"] = {"kwargs": {"room_name": "chat_2_1"}}
        connected, _ = await communicator.connect()
        return communicator, connected

    async def test_connect_authenticated_user(self):
        communicator, connected = await self.connect_to_chat(self.user)
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_receive_message(self):
        communicator, connected = await self.connect_to_chat(self.user)
        self.assertTrue(connected)

        message = {"message": "Hello, world!"}
        await communicator.send_json_to(message)

        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "chat_message")
        self.assertEqual(response["message"], "Hello, world!")
        self.assertEqual(response["sender"], self.user.get_full_name())

        await communicator.disconnect()

    async def test_empty_message(self):
        communicator, connected = await self.connect_to_chat(self.user)
        self.assertTrue(connected)

        await communicator.send_json_to({"message": ""})
        response = await communicator.receive_json_from()
        self.assertIn("error", response)
        self.assertEqual(response["error"], "Empty message is not allowed.")

        await communicator.disconnect()

    async def test_disconnect_and_reconnect(self):
        communicator, connected = await self.connect_to_chat(self.user)
        self.assertTrue(connected)

        await communicator.disconnect()

        communicator, reconnected = await self.connect_to_chat(self.user)
        self.assertTrue(reconnected)

        await communicator.disconnect()

    async def test_invalid_json_payload(self):
        communicator, connected = await self.connect_to_chat(self.user)
        self.assertTrue(connected)

        invalid_payload = "Invalid JSON String"
        await communicator.send_to(text_data=invalid_payload)

        response = await communicator.receive_json_from()
        self.assertIn("error", response)
        self.assertTrue("Invalid JSON format received." in response["error"])

        await communicator.disconnect()

    async def test_join_nonexistent_room(self):
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/api/v1/communications/room/nonexistent_room/"
        )
        communicator.scope["user"] = self.user
        communicator.scope["url_route"] = {"kwargs": {"room_name": "nonexistent_room"}}

        connected, _ = await communicator.connect()

        self.assertFalse(connected)


class ChatAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="user1@gmail.com", password="pass")
        self.user2 = User.objects.create_user(email="user2@gmail.com", password="pass")

    def test_create_conversation(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/v1/communications/conversations/",
            {"online": [self.user1.user_id, self.user2.user_id]},
        )
        self.assertEqual(response.status_code, 201)

    def test_send_message(self):
        room = Room.objects.create()
        room.online.set([self.user1, self.user2])
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/v1/communications/messages/",
            {"room": room.id, "user": self.user1, "content": "Hello!"},
        )
        self.assertEqual(response.status_code, 201)

    def test_message_history(self):
        room = Room.objects.create()
        room.online.set([self.user1, self.user2])
        Message.objects.create(room=room, user=self.user1, content="Hello!")
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(
            f"/api/v1/communications/conversations/{room.id}/messages/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_room_with_invalid_participants(self):
        """Test creating a room with invalid participant data."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/v1/communications/conversations/", {"online": [99999, 88888]}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("online", response.data)

    def test_delete_non_existent_room(self):
        """Test deleting a non-existent room."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete("/api/v1/communications/conversations/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PaginationTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="password"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="password"
        )
        self.room = Room.objects.create(name="Test Room")
        self.room.online.set([self.user1, self.user2])
        response = self.client.post(
            "/auth/jwt/create/",
            {"email": "user1@example.com", "password": "password"},
        )
        self.token = response.data["access"]

        for i in range(11):
            Message.objects.create(
                content=f"Message {i+1}", user=self.user1, room=self.room
            )

    def test_pagination(self):

        response = self.client.get(
            f"/api/v1/communications/conversations/{self.room.id}/messages/",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIn("next", response.data)
        self.assertIsNotNone(response.data["next"])


class MessageValidationTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@gmail.com", password="password1"
        )
        self.user2 = User.objects.create_user(
            email="user2@gmail.com", password="password2"
        )
        self.room = Room.objects.create(name="Test Room")
        self.room.online.add(self.user1, self.user2)
        response = self.client.post(
            "/auth/jwt/create/",
            {"email": "user1@gmail.com", "password": "password1"},
        )
        self.token = response.data["access"]

    def test_user_in_room_can_create_message(self):
        data = {
            "room": self.room.id,
            "user": self.user1,
            "content": "Hello, this is a test message!",
        }
        response = self.client.post(
            f"/api/v1/communications/messages/",
            data=data,
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 201)
        message = Message.objects.last()
        self.assertEqual(message.content, data["content"])
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.user, self.user1)
