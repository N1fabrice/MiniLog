from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from ..models import Entry
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse

class ViewsTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="simba", email="simba@gmail.com", password="simba_123")
        self.user2 = User.objects.create_user(username="fabrice", email="fabrice@gmail.com", password="fabrice_123")

        self.data = {
                "title": "My First Entry",
                "current_mood": "neutral",
                "content": "Today I'm testing my API views."
                }
        self.list_url = reverse("entry-list")

    def test_list_entries(self):
        """
        Testing if authenticated user gets thier own entries, and unauthenticated user gets 401 status code
        """
        # Unauthenticated users get 401 status code
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 401)

        # Login user
        token = RefreshToken.for_user(self.user1).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        # Create entry
        entry_creation = self.client.post(self.list_url, self.data)
        self.assertEqual(entry_creation.status_code, 201)
        
        # Retrieve user's entries
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["user"], self.user1.id)
        
        # Clear credentials
        self.client.credentials()

    def test_retrieve_entry(self):
        """
        Testing single entry retrieval
        """
        # Login user1
        token1 = RefreshToken.for_user(self.user1).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")
        entry_creation = self.client.post(self.list_url, self.data)
        self.assertEqual(entry_creation.status_code, 201)
        entry_id = entry_creation.data["id"]

        # Try retrieving it
        detail_url = reverse("entry-detail", kwargs={"pk": entry_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"], self.user1.id)

        # Switch to user2 and create an entry
        self.client.credentials()
        token2 = RefreshToken.for_user(self.user2).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")

        # user2 should not be able to access user1's entry
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 403)
