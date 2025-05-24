# urls.py
from django.urls import path
from .views import (
    home_view, playlist_detail_view, video_detail_view, 
    my_courses_view, delete_course_view, save_quiz_result_view,
    get_quiz_history_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('playlist/<uuid:pk>/', playlist_detail_view, name='playlist_detail'),
    path("video/<uuid:pk>/", video_detail_view, name="video_detail"),
    path("my-courses/", my_courses_view, name="my_courses"),
    path("delete-course/<uuid:pk>/", delete_course_view, name="delete_course"),
    path("quiz/save-result/", save_quiz_result_view, name="save_quiz_result"),
    path("quiz/history/<uuid:video_id>/", get_quiz_history_view, name="quiz_history"),
]
