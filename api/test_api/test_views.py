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
        self.assertEqual(response.status_code, 404)

    def test_update_entry(self):
        """
        Test that a user can update their own entry and not someone else's
        """
        # Login user1 and create an entry
        token1 = RefreshToken.for_user(self.user1).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")
        entry_creation = self.client.post(self.list_url, self.data)
        self.assertEqual(entry_creation.status_code, 201)
        entry_id = entry_creation.data["id"]

        # Prepare update data
        updated_data = {
            "title": "Updated Title",
            "current_mood": "happy",
            "content": "I updated my entry."
            }

        # Send PUT request
        detail_url = reverse("entry-detail", kwargs={"pk": entry_id})
        response = self.client.put(detail_url, updated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], updated_data["title"])

        # Test unauthenticated user cannot update
        self.client.credentials()  # Clear auth
        response = self.client.put(detail_url, updated_data)
        self.assertEqual(response.status_code, 401)

        # Login as user2 and try updating user1's entry
        token2 = RefreshToken.for_user(self.user2).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")
        response = self.client.put(detail_url, updated_data)
        self.assertEqual(response.status_code, 404)

    def test_delete_entry(self):
        """
        Test deleting an entry:
        - Only the owner can delete it.
        - Others get 404.
        - Unauthenticated users get 401.
        """
        # Login user1 and create an entry
        token = RefreshToken.for_user(self.user1).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        create_response = self.client.post(reverse("entry-list"), self.data)
        self.assertEqual(create_response.status_code, 201)
        entry_id = create_response.data["id"]
        detail_url = reverse("entry-detail", kwargs={"pk": entry_id})
        self.client.credentials()

        # Unauthenticated delete attempt
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 401)

        # Login user2 and try to delete user1's entry
        token = RefreshToken.for_user(self.user2).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 404)
        self.client.credentials()

        # Login user1 and delete their own entry
        token = RefreshToken.for_user(self.user1).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 204)
