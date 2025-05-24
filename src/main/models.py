import uuid
from django.db import models

class Playlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    playlist = models.ForeignKey(Playlist, related_name="videos", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    video_id = models.CharField(max_length=32)
    thumbnail = models.URLField()
    transcript = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    quiz_data = models.JSONField(blank=True, null=True)
