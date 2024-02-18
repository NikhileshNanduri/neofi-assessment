from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Note


class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse("signup")
        self.login_url = reverse("login")
        self.create_note_url = reverse("create_note")
        self.share_note_url = reverse("share_note")
        self.user = User.objects.create_user(
            username="testuser", email="test@neofi.com", password="testpassword"
        )

        self.note = Note.objects.create(content="This is a test note.", owner=self.user)
        self.get_note_url = reverse("get_note", kwargs={"id": self.note.id})
        self.update_note_url = reverse("update_note", kwargs={"id": self.note.id})
        self.get_note_version_history_url = reverse(
            "get_note_version_history", kwargs={"id": self.note.id}
        )

    def test_signup(self):
        data = {
            "username": "newuser",
            "email": "newuser@neofi.com",
            "password": "newpassword",
        }
        response = self.client.post(self.signup_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_create_note(self):
        self.client.force_authenticate(user=self.user)
        data = {"content": "This is a test note."}
        response = self.client.post(self.create_note_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_note(self):
        self.client.force_authenticate(user=self.user)
        note = Note.objects.create(content="This is a test note.", owner=self.user)
        get_note_url_with_id = reverse("get_note", kwargs={"id": note.id})
        response = self.client.get(get_note_url_with_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_share_note(self):
        self.client.force_authenticate(user=self.user)
        shared_user = User.objects.create_user(
            username="shareduser", email="shared@neofi.com", password="sharedpassword"
        )
        data = {"note_id": self.note.id, "shared_users": [shared_user.id]}
        response = self.client.post(self.share_note_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=shared_user)
        shared_user_get_note_url = reverse("get_note", kwargs={"id": self.note.id})
        shared_user_get_note_response = self.client.get(shared_user_get_note_url)
        self.assertEqual(shared_user_get_note_response.status_code, status.HTTP_200_OK)

    def test_update_note(self):
        self.client.force_authenticate(user=self.user)
        updated_content = "Updated content"
        data = {"content": updated_content}
        response = self.client.put(self.update_note_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_note_version_history(self):
        self.client.force_authenticate(user=self.user)
        initial_content = "Initial content"
        initial_data = {"content": initial_content}
        response = self.client.post(self.create_note_url, initial_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        updated_content_1 = "Updated content 1"
        update_data_1 = {"content": updated_content_1}
        response = self.client.put(self.update_note_url, update_data_1, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_content_2 = "Updated content 2"
        update_data_2 = {"content": updated_content_2}
        response = self.client.put(self.update_note_url, update_data_2, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_content_2 = "Updated content 3"
        update_data_2 = {"content": updated_content_2}
        response = self.client.put(self.update_note_url, update_data_2, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.get_note_version_history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
