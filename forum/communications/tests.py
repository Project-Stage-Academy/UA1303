from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import status

from channels.testing import ChannelsLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .models import Room, Message
from .serializers import MessageSerializer


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


# class ChatTests(ChannelsLiveServerTestCase):
#     serve_static = True  # emulate StaticLiveServerTestCase

#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         try:
#             # NOTE: Requires "chromedriver" binary to be installed in $PATH
#             cls.driver = webdriver.Chrome()
#         except Exception as e:
#             super().tearDownClass()
#             raise RuntimeError(f"Failed to initialize WebDriver: {e}")

#     @classmethod
#     def tearDownClass(cls):
#         if hasattr(cls, "driver") and cls.driver:
#             cls.driver.quit()
#         super().tearDownClass()

#     def test_when_chat_message_posted_then_seen_by_everyone_in_same_room(self):
#         self._test_message_exchange(
#             room_1="room_1", room_2="room_1", expected_shared=True
#         )

#     def test_when_chat_message_posted_then_not_seen_by_anyone_in_different_room(self):
#         self._test_message_exchange(
#             room_1="room_1", room_2="room_2", expected_shared=False
#         )

#     # === Utility ===

#     def _test_message_exchange(self, room_1, room_2, expected_shared):
#         """Utility to test message exchange between different rooms."""
#         try:
#             self._enter_chat_room(room_1)
#             self._open_new_window()
#             self._enter_chat_room(room_2)

#             # Post message in first window
#             self._switch_to_window(0)
#             message_1 = "hello"
#             self._post_message(message_1)
#             self._wait_for_message(message_1)

#             # Post message in second window
#             self._switch_to_window(1)
#             message_2 = "world"
#             self._post_message(message_2)
#             self._wait_for_message(message_2)

#             # Verify message visibility
#             if expected_shared:
#                 self.assertIn(
#                     message_1,
#                     self._chat_log_value,
#                     f"Message '{message_1}' not shared correctly.",
#                 )
#             else:
#                 self.assertNotIn(
#                     message_1,
#                     self._chat_log_value,
#                     f"Message '{message_1}' improperly shared between rooms.",
#                 )
#         finally:
#             self._close_all_new_windows()

#     def _enter_chat_room(self, room_name):
#         self.driver.get(f"{self.live_server_url}/api/v1/communications/")
#         room_input = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "room-name-input")),
#             "Room input field not found",
#         )
#         room_input.clear()
#         room_input.send_keys(room_name, Keys.ENTER)
#         WebDriverWait(self.driver, 10).until(
#             lambda driver: room_name in driver.current_url,
#             "Failed to navigate to the chat room",
#         )

#     def _open_new_window(self):
#         self.driver.execute_script('window.open("about:blank", "_blank");')
#         self._switch_to_window(-1)

#     def _close_all_new_windows(self):
#         while len(self.driver.window_handles) > 1:
#             self._switch_to_window(-1)
#             self.driver.close()
#         self._switch_to_window(0)

#     def _switch_to_window(self, window_index):
#         self.driver.switch_to.window(self.driver.window_handles[window_index])

#     # def _post_message(self, message):
#     #     chat_input = WebDriverWait(self.driver, 10).until(
#     #         EC.presence_of_element_located((By.ID, "chat-message-input")),
#     #         "Chat message input field not found",
#     #     )
#     #     chat_input.clear()
#     #     chat_input.send_keys(message, Keys.ENTER)

#     def _post_message(self, message):
#         # Чекаємо на наявність елемента для введення повідомлення
#         chat_input = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "chat-message-input")),
#             "Chat log input field not found",
#         )

#         # Якщо div має атрибут contenteditable, можна використати textContent
#         self.driver.execute_script("arguments[0].textContent = arguments[1];", chat_input, message)

#         # Тепер натискаємо кнопку відправлення
#         send_button = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "chat-message-submit")),
#             "Send button not found",
#         )
#         send_button.click()

#     def _wait_for_message(self, message):
#         WebDriverWait(self.driver, 10).until(
#             lambda driver: message in self._chat_log_value,
#             f"Message '{message}' was not received",
#         )

#     @property
#     def _chat_log_value(self):
#         chat_log = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "chat-log")),
#             "Chat log element not found",
#         )
#         return chat_log.text
#     # @property
#     # def _chat_log_value(self):
#     #     chat_log = WebDriverWait(self.driver, 10).until(
#     #         EC.presence_of_element_located((By.ID, "chat-log")),
#     #         "Chat log element not found",
#     #     )
#     #     return chat_log.get_property("value")


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
