from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Playlist, Video, QuizAttempt, QuizAnswer
import sys
import os
import json

# Ensure src directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fetch_playlist import get_playlist_title

def get_user_session(request):
    """Get or create a session ID for anonymous users"""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

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
    user_session = get_user_session(request)
    
    # Get all videos for this playlist with quiz progress
    videos = Video.objects.filter(playlist=playlist)
    video_progress = {}
    
    for video in videos:
        # Get the latest quiz attempt for this video
        latest_attempt = QuizAttempt.objects.filter(
            video=video, 
            user_session=user_session
        ).first()
        
        video_progress[str(video.id)] = {
            'has_quiz': bool(video.quiz_data),
            'attempted': bool(latest_attempt),
            'passed': latest_attempt.is_passed if latest_attempt else False,
            'score': latest_attempt.percentage if latest_attempt else 0,
            'last_attempt': latest_attempt.completed_at if latest_attempt else None
        }
    
    return render(request, "main/playlist_detail.html", {
        "playlist_id": playlist.id,
        "playlist_url": playlist.url,
        "video_progress": video_progress,
    })


def video_detail_view(request, pk):
    video = Video.objects.get(pk=pk)
    user_session = get_user_session(request)
    
    # Serialize quiz data to JSON string for the template
    quiz_data_json = None
    if video.quiz_data:
        quiz_data_json = json.dumps(video.quiz_data)
    
    # Get quiz attempts for this video
    quiz_attempts = QuizAttempt.objects.filter(
        video=video, 
        user_session=user_session
    )
    
    # Get the best attempt
    best_attempt = quiz_attempts.filter(is_passed=True).first()
    if not best_attempt:
        best_attempt = quiz_attempts.first()
    
    return render(request, "main/video_detail.html", {
        "video": video,
        "quiz_data_json": quiz_data_json,
        "quiz_attempts": quiz_attempts,
        "best_attempt": best_attempt,
        "user_session": user_session,
    })


@csrf_exempt
@require_http_methods(["POST"])
def save_quiz_result_view(request):
    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        answers = data.get('answers', [])
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 0)
        
        user_session = get_user_session(request)
        video = get_object_or_404(Video, pk=video_id)
        
        # Calculate percentage and determine if passed
        percentage = (score / total_questions * 100) if total_questions > 0 else 0
        is_passed = percentage >= 60  # 60% to pass
        
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            video=video,
            user_session=user_session,
            score=score,
            total_questions=total_questions,
            percentage=percentage,
            is_passed=is_passed
        )
        
        # Save individual answers
        for answer_data in answers:
            QuizAnswer.objects.create(
                attempt=attempt,
                question_index=answer_data.get('question_index', 0),
                question_text=answer_data.get('question_text', ''),
                selected_option=answer_data.get('selected_option', 0),
                selected_text=answer_data.get('selected_text', ''),
                correct_option=answer_data.get('correct_option', 0),
                correct_text=answer_data.get('correct_text', ''),
                is_correct=answer_data.get('is_correct', False)
            )
        
        return JsonResponse({
            'success': True,
            'attempt_id': str(attempt.id),
            'percentage': percentage,
            'is_passed': is_passed
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def get_quiz_history_view(request, video_id):
    user_session = get_user_session(request)
    video = get_object_or_404(Video, pk=video_id)
    
    attempts = QuizAttempt.objects.filter(
        video=video,
        user_session=user_session
    ).prefetch_related('answers')
    
    attempts_data = []
    for attempt in attempts:
        answers_data = []
        for answer in attempt.answers.all():
            answers_data.append({
                'question_index': answer.question_index,
                'question_text': answer.question_text,
                'selected_option': answer.selected_option,
                'selected_text': answer.selected_text,
                'correct_option': answer.correct_option,
                'correct_text': answer.correct_text,
                'is_correct': answer.is_correct
            })
        
        attempts_data.append({
            'id': str(attempt.id),
            'score': attempt.score,
            'total_questions': attempt.total_questions,
            'percentage': attempt.percentage,
            'is_passed': attempt.is_passed,
            'completed_at': attempt.completed_at.isoformat(),
            'answers': answers_data
        })
    
    return JsonResponse({
        'attempts': attempts_data,
        'video_title': video.title
    })


def my_courses_view(request):
    # Get all playlists from the database
    playlists = Playlist.objects.all().order_by('-created_at')
    user_session = get_user_session(request)
    
    # For each playlist, get the count of videos and progress
    for playlist in playlists:
        videos = Video.objects.filter(playlist=playlist)
        playlist.video_count = videos.count()
        
        # Calculate progress
        videos_with_quiz = videos.filter(quiz_data__isnull=False)
        playlist.quiz_count = videos_with_quiz.count()
        
        # Count passed quizzes
        passed_count = 0
        for video in videos_with_quiz:
            latest_attempt = QuizAttempt.objects.filter(
                video=video, 
                user_session=user_session,
                is_passed=True
            ).first()
            if latest_attempt:
                passed_count += 1
        
        playlist.passed_count = passed_count
        playlist.progress_percentage = (passed_count / playlist.quiz_count * 100) if playlist.quiz_count > 0 else 0
    
    return render(request, "main/my_courses.html", {"playlists": playlists})


def delete_course_view(request, pk):
    # Get the playlist or return 404 if not found
    playlist = get_object_or_404(Playlist, pk=pk)
    
    # Delete the playlist (will cascade delete all related videos)
    playlist.delete()
    
    # Redirect back to my courses page
    return redirect('my_courses')