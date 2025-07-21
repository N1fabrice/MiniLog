from rest_framework.test import APITestCase
from ..serializers import EntrySerializer
from ..models import Entry
from django.contrib.auth.models import User

class SerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="john", email="john@gmail.com", password="john_123")

    def test_valid_data_serialization(self):
        """
        Testing that entry is saved and the fields match what was sent.
        """
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

    def test_missing_field(self):
        """
        Testing whether validation works with missing fields.
        """
        invalid_data = {
            "current_mood": "happy",
            "content": "Lets see if it works"
            }
        serializer = EntrySerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_readonly_field(self):
        """
        Testing read-only field 'user' is ignored during input.
        """
        valid_data = {
            "user": 99,
            "title": "My title",
            "current_mood": "happy",
            "content": "Lets see if it works"
            }
        serializer = EntrySerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn("user", serializer.validated_data)

    def test_serialization_output(self):
        """
        Testing if all expected fields are present and are in the correct format.
        """
        entry = Entry.objects.create(
                user=self.user,
                title="My title",
                current_mood="neutral",
                content="Running tests."
                )
        serializer = EntrySerializer(instance=entry)
        data = serializer.data
        self.assertIn("user", data)
        self.assertEqual(data["user"], self.user.id)
        self.assertIn("title", data)
        self.assertEqual(data["title"], entry.title)
        self.assertIn("current_mood", data)
        self.assertEqual(data["current_mood"], entry.current_mood)
        self.assertIn("content", data)
        self.assertEqual(data["content"], entry.content)
