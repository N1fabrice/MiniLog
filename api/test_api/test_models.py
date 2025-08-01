from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Entry
from django.urls import reverse

class EntryCreateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="john", email="john@gmail.com", password="john_123")
        token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.url = reverse("entry-list")

    def test_create_entry(self):
        """
        Testing creating an entry(model instance)
        """
        data = {
                "title": "My First Entry",
                "current_mood": "neutral",
                "content": "Today I started testing my API."
                }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "My First Entry")
        self.assertEqual(response.data["current_mood"], "neutral")
        self.assertEqual(response.data["content"], "Today I started testing my API.")

    def test_update_entry(self):
        """
        Testing updating an entry
        """
        data1 = {
                 "title": "Testing Updating Entry",
                "current_mood": "neutral",
                "content": "Today I started testing my API models."
                }

        data2 = {
                 "title": "Updating Works",
                "current_mood": "happy",
                "content": "Today I started testing my API models."
                }

        response1 = self.client.post(self.url, data1)
        self.assertEqual(response1.status_code, 201)
        entry_id = response1.data["id"]


        detail_url = reverse("entry-detail", kwargs={"pk": entry_id})
        response2 = self.client.put(detail_url, data2)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data["title"], "Updating Works")
        self.assertEqual(response2.data["current_mood"], "happy")

    def test_delete_entry(self):
        """
        Testing deleting an entry
        """
        data = {
                 "title": "My First Entry",
                "current_mood": "neutral",
                "content": "Today I started testing my API."
                }

        response1 = self.client.post(self.url, data)
        self.assertEqual(response1.status_code, 201)
        response1_id = response1.data["id"]

        detail_url = reverse("entry-detail", kwargs={"pk": response1_id})
        response2 = self.client.delete(detail_url)

        self.assertEqual(response2.status_code, 204)
        self.assertEqual(self.client.get(detail_url).status_code, 404)
    

    def test_str_entry(self):
        """
        Testing string representation
        """
        data = {
                 "title": "My First Entry",
                "current_mood": "neutral",
                "content": "Today I started testing my API."
                }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)

        entry = Entry.objects.first()
        expected_str = f"{entry.title} - {entry.date}"
        self.assertEqual(str(entry), expected_str)

    def test_entry_constraints(self):
        """
        Testing blank=False contraint on the entry fields
        """
        data1 = {
                "title": "",
                "current_mood": "",
                "content": ""
                }
        response1 = self.client.post(self.url, data1)
        self.assertEqual(response1.status_code, 400)

        data2 = {
                "title": "Title",
                "current_mood": "happy",
                "content": ""
                }
        response2 = self.client.post(self.url, data2)
        self.assertEqual(response2.status_code, 400)
