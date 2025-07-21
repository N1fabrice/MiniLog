from rest_framework.test import APITestCase
from ..serializers import EntrySerializer
from ..models import Entry
from django.contrib.auth.models import User

class SerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="john", email="john@gmail.com", password="john_123")

    def test_valid_data_serialization(self):
        valid_data = {
            "title": "My title",
            "current_mood": "happy",
            "content": "Lets see if it works"
            }
        serializer = EntrySerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        entry = serializer.save(user=self.user)
        self.assertEqual(entry.title, valid_data["title"])
        self.assertEqual(entry.current_mood, valid_data["current_mood"])
        self.assertEqual(entry.content, valid_data["content"])
        self.assertEqual(entry.user, self.user)
