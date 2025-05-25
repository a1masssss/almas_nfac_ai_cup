import uuid
from django.db import models
from django.contrib.auth.models import User

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
    order = models.PositiveIntegerField(default=0)  # Order of video in playlist

    class Meta:
        ordering = ['order']


class QuizAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, related_name="quiz_attempts", on_delete=models.CASCADE)
    user_session = models.CharField(max_length=255)  # For anonymous users
    score = models.IntegerField()  # Number of correct answers
    total_questions = models.IntegerField()
    percentage = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)
    is_passed = models.BooleanField(default=False)  # True if score >= 60%

    class Meta:
        ordering = ['-completed_at']


class QuizAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(QuizAttempt, related_name="answers", on_delete=models.CASCADE)
    question_index = models.IntegerField()
    question_text = models.TextField()
    selected_option = models.IntegerField()
    selected_text = models.TextField()
    correct_option = models.IntegerField()
    correct_text = models.TextField()
    is_correct = models.BooleanField()

    class Meta:
        ordering = ['question_index']
