from django.db import models
from django.contrib.auth.models import User
# Create your models here.

mood = {
        "happy": "Happy",
        "sad": "Sad",
        "excited": "Excited",
        "stressed": "Stressed",
        "neutral": "Neutral"
        }

class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="entries")
    date = models.DateField(auto_now_add=True),
    title = models.CharField()
    content = models.TextField()
    current_mood = models.CharField(choices=mood)

    def __str__(self):
        return f"{self.title} - self.date"
