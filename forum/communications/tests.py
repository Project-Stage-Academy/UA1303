from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from unittest.mock import patch, MagicMock
from rest_framework_simplejwt.tokens import RefreshToken
from channels.testing import WebsocketCommunicator
from .factories import *
from .models import Room, Message
from mongoengine.connection import get_db
from bson import ObjectId

from django.test import TestCase
from channels.testing import WebsocketCommunicator
from communications.consumers import ChatConsumer
from mongoengine import connect, disconnect
from communications.models import Room

User = get_user_model()


class TestChatConsumer(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        disconnect()
        connect("forum_database_mongo_test", host="mongodb://localhost:27017")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        db = get_db()
        db.client.drop_database("forum_database_mongo_test")
        disconnect()

    def setUp(self):
        self.user1 = User1Factory()
        self.user2 = User2Factory()

        self.room = Room(
            name="room_1_2", participants=[self.user1.user_id, self.user2.user_id]
        )
        self.room.save()

    async def connect_to_chat(self, user):
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/api/v1/communications/room/room_1_2/"
        )
        communicator.scope["user"] = user
        communicator.scope["url_route"] = {"kwargs": {"room_name": "room_1_2"}}
        connected, _ = await communicator.connect()
        return communicator, connected

    async def test_connect_authenticated_user(self):
        communicator, connected = await self.connect_to_chat(self.user1)
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_receive_message(self):
        communicator, connected = await self.connect_to_chat(self.user1)
        self.assertTrue(connected)

        message = {"message": "Hello, world!"}
        await communicator.send_json_to(message)

        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "chat_message")
        self.assertEqual(response["message"], "Hello, world!")
        self.assertEqual(response["sender"], self.user1.get_full_name())

        await communicator.disconnect()

    async def test_empty_message(self):
        communicator, connected = await self.connect_to_chat(self.user1)
        self.assertTrue(connected)

        await communicator.send_json_to({"message": ""})
        response = await communicator.receive_json_from()
        self.assertIn("error", response)
        self.assertEqual(response["error"], "Empty message is not allowed.")

        await communicator.disconnect()

    async def test_disconnect_and_reconnect(self):
        communicator, connected = await self.connect_to_chat(self.user1)
        self.assertTrue(connected)

        await communicator.disconnect()

        communicator, reconnected = await self.connect_to_chat(self.user1)
        self.assertTrue(reconnected)

        await communicator.disconnect()

    async def test_invalid_json_payload(self):
        communicator, connected = await self.connect_to_chat(self.user1)
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
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {"kwargs": {"room_name": "nonexistent_room"}}

        connected, _ = await communicator.connect()

        self.assertFalse(connected)


class RoomModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        disconnect()
        connect("forum_database_mongo_test", host="mongodb://localhost:27017")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        db = get_db()
        db.client.drop_database("forum_database_mongo_test")
        disconnect()

    def setUp(self):
        self.user1 = User1Factory()
        self.user2 = User2Factory()
        self.room = Room(
            name="room_1_2", participants=[self.user1.user_id, self.user2.user_id]
        )
        self.room.save()

    def test_room_name(self):
        self.assertEqual(self.room.name, "room_1_2")

    def test_join_user(self):
        self.room.join(self.user1)
        self.assertIn(self.user1.user_id, self.room.participants)

    def test_leave_user(self):
        self.room.join(self.user1)
        self.room.leave(self.user1)
        self.assertNotIn(self.user1.user_id, self.room.participants)

    def test_get_users_id(self):
        self.assertEqual(
            self.room.participants, [self.user1.user_id, self.user2.user_id]
        )

    # def test_get_users_names(self):

    #     self.room.name = f"room_{self.user1.user_id}_{self.user2.user_id}"
    #     self.room.save()
    #     self.room.online.set([self.user1, self.user2])

    #     expected_names = {
    #         "user_1": self.user1.first_name,
    #         "user_2": self.user2.first_name,
    #     }
    #     self.assertEqual(self.room.get_users_names(), expected_names)

    def test_leave_nonexistent_user(self):
        self.room.leave(self.user1)
        self.assertNotIn(self.user1, self.room.participants)

    # def test_get_online_count_empty_room(self):
    #     self.assertEqual(self.room.get_online_count(), 0)

    def test_message_encryption(self):
        message = Message(user=self.user1, content="Hello!")
        self.assertEqual(message.content, "Hello!")

    # def test_message_max_length(self):
    #     long_message = "x" * 513
    #     with self.assertRaises(ValueError):
    #         Message(user=self.user1, content=long_message)


class ChatAPITests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        disconnect()
        connect("forum_database_mongo_test", host="mongodb://localhost:27017")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        db = get_db()
        db.client.drop_database("forum_database_mongo_test")
        disconnect()

    def setUp(self):
        self.user1 = User1Factory()
        self.user2 = User2Factory()
        self.room = Room(
            name="room_1_2", participants=[self.user1.user_id, self.user2.user_id]
        )
        self.room.save()

    def test_create_conversation(self):
        Room.objects.all().delete()
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/v1/communications/conversations/",
            {"participants": [self.user1.user_id, self.user2.user_id]},
        )
        self.assertEqual(response.status_code, 201)

    def test_send_message(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            f"/api/v1/communications/{ObjectId(self.room.id)}/messages/",
            {"user": self.user1.user_id, "content": "Hello!"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_message_history(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            f"/api/v1/communications/{ObjectId(self.room.id)}/messages/",
            {"user": self.user1.user_id, "content": "Hello!"},
            format="json",
        )
        response = self.client.get(
            f"/api/v1/communications/conversations/{ObjectId(self.room.id)}/messages/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_room_with_invalid_participants(self):
        """Test creating a room with invalid participant data."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/v1/communications/conversations/", {"participants": [99999, 88888]}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("participants", response.data)
        self.assertEqual(
            response.json()["participants"][0],
            "You must include yourself as a participant.",
        )

    def test_delete_non_existent_room(self):  # This need a fix
        """Test deleting a non-existent room."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete("/api/v1/communications/conversations/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PaginationTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        disconnect()
        connect("forum_database_mongo_test", host="mongodb://localhost:27017")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        db = get_db()
        db.client.drop_database("forum_database_mongo_test")
        disconnect()

    def setUp(self):
        self.user1 = User1Factory()
        self.user2 = User2Factory()
        self.room = Room(
            name="room_1_2", participants=[self.user1.user_id, self.user2.user_id]
        )
        self.room.save()
        self.client.force_authenticate(user=self.user1)
        for i in range(10):
            self.client.post(
                f"/api/v1/communications/{ObjectId(self.room.id)}/messages/",
                {"user": self.user1.user_id, "content": "Hello!"},
                format="json",
            )

    def tearDown(self):
        return super().tearDown()

    def test_pagination(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(
            f"/api/v1/communications/conversations/{ObjectId(self.room.id)}/messages/",
        )
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIn("next", response.data)
        self.assertIsNone(response.data["next"])

    def test_pagination_fewer_than_ten_messages(self):

        for i in range(5):
            self.client.post(
                f"/api/v1/communications/{ObjectId(self.room.id)}/messages/",
                {"user": self.user1.user_id, "content": "Hello!"},
                format="json",
            )

        response = self.client.get(
            f"/api/v1/communications/conversations/{ObjectId(self.room.id)}/messages/"
        )
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertEqual(response.data["next"], None)

    # def test_pagination_last_page(self):
    #     response = self.client.get(
    #         f"/api/v1/communications/conversations/{self.room.id}/messages/?page=2",
    #         HTTP_AUTHORIZATION=f"Bearer {self.token}",
    #     )

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn("results", response.data)
    #     self.assertEqual(len(response.data["results"]), 1)
    #     self.assertEqual(response.data["next"], None)

    # def test_pagination_invalid_page_number(self):
    #     response = self.client.get(
    #         f"/api/v1/communications/conversations/{self.room.id}/messages/?page=999",
    #         HTTP_AUTHORIZATION=f"Bearer {self.token}",
    #     )

    #     self.assertEqual(response.status_code, 404)
    #     self.assertIn("detail", response.data)
    #     self.assertEqual(response.data["detail"], "Invalid page.")


# class MessageValidationTests(APITestCase):
#     def setUp(self):
#         self.user1 = User1Factory()
#         self.user2 = User2Factory()
#         self.room = Room(
#             name="room_1_2", participants=[self.user1.user_id, self.user2.user_id]
#         )
#         self.room.online.add(self.user1, self.user2)

#         refresh = RefreshToken.for_user(self.user1)
#         self.token = str(refresh.access_token)

#     @patch("rest_framework_simplejwt.tokens.RefreshToken.for_user")
#     def test_jwt_mocked(self, mock_refresh_token):
#         mocked_token = MagicMock()
#         mocked_token.access_token = "mocked_access_token"
#         mock_refresh_token.return_value = mocked_token

#         response = self.client.post(
#             "/auth/jwt/create/", {"email": self.user1.email, "password": "password1"}
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data["access"], "mocked_access_token")

#     def test_user_in_room_can_create_message(self):
#         data = {
#             "room": self.room.id,
#             "user": self.user1.user_id,
#             "content": "Hello, this is a test message!",
#         }
#         response = self.client.post(
#             "/api/v1/communications/messages/",
#             data=data,
#             HTTP_AUTHORIZATION=f"Bearer {self.token}",
#         )
#         self.assertEqual(response.status_code, 201)
#         message = Message.objects.last()
#         self.assertEqual(message.content, data["content"])
#         self.assertEqual(message.room, self.room)
#         self.assertEqual(message.user, self.user1)
