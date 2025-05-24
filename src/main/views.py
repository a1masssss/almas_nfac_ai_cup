from django.shortcuts import redirect, render, get_object_or_404
from .models import Playlist, Video
import sys
import os

# Ensure src directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fetch_playlist import get_playlist_title

def home_view(request):
    if request.method == "POST":
        playlist_url = request.POST.get("playlist")
        if not playlist_url:
            return render(request, "main/main.html", {"error": "No playlist provided."})

        # Create the playlist in the database
        playlist = Playlist.objects.create(url=playlist_url)
        
        # Try to get the title immediately
        try:
            title = get_playlist_title(playlist_url)
            if title:
                playlist.title = title
                playlist.save()
        except Exception:
            # If we can't get the title now, the WebSocket will try later
            pass
            
        return redirect("playlist_detail", pk=playlist.id)
    
    return render(request, "main/main.html")


def playlist_detail_view(request, pk):
    playlist = Playlist.objects.get(pk=pk)
    return render(request, "main/playlist_detail.html", {
        "playlist_id": playlist.id,
        "playlist_url": playlist.url,
    })


def video_detail_view(request, pk):
    video = Video.objects.get(pk=pk)
    
    # Serialize quiz data to JSON string for the template
    quiz_data_json = None
    if video.quiz_data:
        import json
        quiz_data_json = json.dumps(video.quiz_data)
    
    return render(request, "main/video_detail.html", {
        "video": video,
        "quiz_data_json": quiz_data_json
    })


def my_courses_view(request):
    # Get all playlists from the database
    playlists = Playlist.objects.all().order_by('-created_at')
    
    # For each playlist, get the count of videos
    for playlist in playlists:
        playlist.video_count = Video.objects.filter(playlist=playlist).count()
    
    return render(request, "main/my_courses.html", {"playlists": playlists})


def delete_course_view(request, pk):
    # Get the playlist or return 404 if not found
    playlist = get_object_or_404(Playlist, pk=pk)
    
    # Delete the playlist (will cascade delete all related videos)
    playlist.delete()
    
    # Redirect back to my courses page
    return redirect('my_courses')