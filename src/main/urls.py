# urls.py
from django.urls import path
from .views import home_view, playlist_detail_view, video_detail_view, my_courses_view, delete_course_view

urlpatterns = [
    path('', home_view, name='home'),
    path('playlist/<uuid:pk>/', playlist_detail_view, name='playlist_detail'),
    path("video/<uuid:pk>/", video_detail_view, name="video_detail"),
    path("my-courses/", my_courses_view, name="my_courses"),
    path("delete-course/<uuid:pk>/", delete_course_view, name="delete_course"),
]
