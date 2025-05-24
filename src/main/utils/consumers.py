import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from fetch_playlist import fetch_playlist_videos, fetch_transcript, get_playlist_title
from main.gemini_summarizer import summarize_with_chatgpt, generate_quiz_questions

class PlaylistConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        from main.models import Playlist, Video

        data = json.loads(text_data)
        action = data.get("action", "process_playlist")

        if action == "process_playlist":
            await self.process_playlist(data)
        elif action == "get_quiz":
            await self.get_quiz(data)
        elif action == "submit_answer":
            await self.submit_answer(data)

    async def process_playlist(self, data):
        from main.models import Playlist, Video

        playlist_id = data.get("playlist_id")

        try:
            playlist = await sync_to_async(Playlist.objects.get)(pk=playlist_id)
            playlist_url = playlist.url
        except Playlist.DoesNotExist:
            await self.send(json.dumps({"type": "error", "message": "Playlist not found"}))
            return

        # Get playlist title and send it immediately
        playlist_title = await sync_to_async(get_playlist_title)(playlist_url)
        
        # Save the title to the playlist model
        if playlist_title and not playlist.title:
            playlist.title = playlist_title
            await sync_to_async(playlist.save)()
            
        await self.send(json.dumps({
            "type": "playlist_info",
            "title": playlist_title or "YouTube Playlist",
            "url": playlist_url
        }))

        # Find existing videos for this playlist
        existing_videos = await sync_to_async(list)(
            Video.objects.filter(playlist=playlist)
        )
        
        # Send existing videos to the client immediately
        for v in existing_videos:
            await self.send(json.dumps({
                "type": "video",
                "id": str(v.id),
                "title": v.title,
                "thumbnail": v.thumbnail,
                "has_quiz": bool(v.quiz_data)
            }))

        # If we already have videos for this playlist, we don't need to fetch more
        if existing_videos:
            # Just notify that processing is complete
            await self.send(json.dumps({"type": "processing_complete"}))
            return

        # No videos yet, so fetch them from YouTube
        videos = await sync_to_async(fetch_playlist_videos)(playlist_url)

        for video_data in videos:
            # Check if this video already exists in the database (to avoid duplicates)
            existing_video = await sync_to_async(
                lambda: Video.objects.filter(playlist=playlist, video_id=video_data["id"]).first()
            )()
            
            if existing_video:
                # Skip this video as it's already in the database
                continue
                
            # Create new video in the database
            video_obj = await sync_to_async(Video.objects.create)(
                playlist=playlist,
                title=video_data["title"],
                video_id=video_data["id"],
                thumbnail=f'https://img.youtube.com/vi/{video_data["id"]}/maxresdefault.jpg'
            )

            # Get and store transcript and summary
            await self.send(json.dumps({
                "type": "processing_status",
                "message": f"📝 Fetching transcript for: {video_data['title'][:50]}..."
            }))
            
            transcript = await sync_to_async(fetch_transcript)(video_data["id"])
            
            await self.send(json.dumps({
                "type": "processing_status",
                "message": f"🤖 Creating summary for: {video_data['title'][:50]}..."
            }))
            
            summary = await sync_to_async(summarize_with_chatgpt)(transcript[:50000])

            # Generate quiz
            await self.send(json.dumps({
                "type": "processing_status",
                "message": f"🧠 Generating quiz for: {video_data['title'][:50]}..."
            }))
            
            quiz_data = None
            try:
                # Generate quiz with improved error handling
                quiz_json = await sync_to_async(generate_quiz_questions)(summary, video_data["title"])
                
                # Multiple cleaning attempts for robust JSON parsing
                original_quiz_json = quiz_json
                
                # Step 1: Remove markdown formatting
                quiz_json = quiz_json.strip()
                if quiz_json.startswith('```json'):
                    quiz_json = quiz_json[7:]
                elif quiz_json.startswith('```'):
                    quiz_json = quiz_json[3:]
                if quiz_json.endswith('```'):
                    quiz_json = quiz_json[:-3]
                quiz_json = quiz_json.strip()
                
                # Step 2: Remove any leading/trailing whitespace and newlines
                quiz_json = quiz_json.strip('\n\r\t ')
                
                # Step 3: Ensure it starts with { and ends with }
                if not quiz_json.startswith('{'):
                    # Try to find the first {
                    start_idx = quiz_json.find('{')
                    if start_idx != -1:
                        quiz_json = quiz_json[start_idx:]
                    else:
                        raise ValueError("No valid JSON object found")
                
                if not quiz_json.endswith('}'):
                    # Try to find the last }
                    end_idx = quiz_json.rfind('}')
                    if end_idx != -1:
                        quiz_json = quiz_json[:end_idx + 1]
                    else:
                        raise ValueError("No valid JSON object found")
                
                # Step 4: Parse and validate the JSON
                quiz_data = json.loads(quiz_json)
                
                # Step 5: Comprehensive validation
                if not isinstance(quiz_data, dict):
                    raise ValueError("Quiz data must be a dictionary")
                
                if 'questions' not in quiz_data:
                    raise ValueError("Quiz data missing 'questions' key")
                
                if not isinstance(quiz_data['questions'], list):
                    raise ValueError("'questions' must be a list")
                
                if len(quiz_data['questions']) == 0:
                    raise ValueError("Quiz must have at least 1 question")
                
                # Validate and fix each question
                valid_questions = []
                for i, question in enumerate(quiz_data['questions']):
                    try:
                        if not isinstance(question, dict):
                            print(f"Skipping question {i}: not a dictionary")
                            continue
                        
                        if 'question' not in question or 'options' not in question:
                            print(f"Skipping question {i}: missing required fields")
                            continue
                        
                        if not isinstance(question['options'], list):
                            print(f"Skipping question {i}: options not a list")
                            continue
                        
                        if len(question['options']) < 2:
                            print(f"Skipping question {i}: less than 2 options")
                            continue
                        
                        # Ensure each option has required fields
                        valid_options = []
                        correct_count = 0
                        
                        for j, option in enumerate(question['options']):
                            if not isinstance(option, dict):
                                continue
                            if 'text' not in option:
                                continue
                            
                            # Ensure correct field exists
                            if 'correct' not in option:
                                option['correct'] = False
                            
                            if option['correct']:
                                correct_count += 1
                            
                            valid_options.append(option)
                        
                        # Ensure exactly one correct answer
                        if correct_count == 0 and valid_options:
                            valid_options[0]['correct'] = True
                        elif correct_count > 1:
                            # Keep only the first correct answer
                            found_correct = False
                            for option in valid_options:
                                if option['correct'] and found_correct:
                                    option['correct'] = False
                                elif option['correct']:
                                    found_correct = True
                        
                        if len(valid_options) >= 2:
                            question['options'] = valid_options
                            valid_questions.append(question)
                        
                    except Exception as e:
                        print(f"Error validating question {i}: {e}")
                        continue
                
                if len(valid_questions) == 0:
                    raise ValueError("No valid questions found after validation")
                
                quiz_data['questions'] = valid_questions
                print(f"Successfully generated and validated quiz with {len(valid_questions)} questions")
                
            except Exception as e:
                print(f"Error generating quiz for {video_data['title']}: {e}")
                if 'original_quiz_json' in locals():
                    print(f"Original AI response: {original_quiz_json}")
                if 'quiz_json' in locals():
                    print(f"Cleaned response: {quiz_json}")
                
                # Create a comprehensive fallback quiz
                quiz_data = {
                    "questions": [
                        {
                            "question": f"What is the main topic of the lesson '{video_data['title']}'?",
                            "options": [
                                {"text": "The primary subject matter covered in this educational video", "correct": True},
                                {"text": "Unrelated topic about cooking techniques", "correct": False},
                                {"text": "Information about sports and fitness", "correct": False}
                            ]
                        },
                        {
                            "question": "What type of learning approach is most effective for this content?",
                            "options": [
                                {"text": "Active engagement and practical application of concepts", "correct": True},
                                {"text": "Passive listening without taking any notes", "correct": False},
                                {"text": "Skipping the content entirely", "correct": False}
                            ]
                        },
                        {
                            "question": "Why is it important to understand the concepts presented in this lesson?",
                            "options": [
                                {"text": "To gain valuable knowledge and develop relevant skills", "correct": True},
                                {"text": "To memorize facts without understanding their application", "correct": False},
                                {"text": "To pass time without learning anything meaningful", "correct": False}
                            ]
                        },
                        {
                            "question": "How can you best apply what you've learned from this lesson?",
                            "options": [
                                {"text": "Practice the concepts and integrate them into real-world scenarios", "correct": True},
                                {"text": "Forget about it immediately after watching", "correct": False},
                                {"text": "Only use the information for test-taking purposes", "correct": False}
                            ]
                        }
                    ]
                }
                print("Using fallback quiz due to generation/parsing errors")

            # Update the video with transcript, summary and quiz
            video_obj.transcript = transcript
            video_obj.summary = summary
            video_obj.quiz_data = quiz_data
            await sync_to_async(video_obj.save)()

            # Send the new video to the client
            await self.send(json.dumps({
                "type": "video",
                "id": str(video_obj.id),
                "title": video_obj.title,
                "thumbnail": video_obj.thumbnail,
                "has_quiz": bool(quiz_data)
            }))
            
        # Notify that processing is complete
        await self.send(json.dumps({"type": "processing_complete"}))

    async def get_quiz(self, data):
        from main.models import Video

        video_id = data.get("video_id")
        
        try:
            video = await sync_to_async(Video.objects.get)(pk=video_id)
            
            if video.quiz_data:
                await self.send(json.dumps({
                    "type": "quiz_data",
                    "video_id": str(video.id),
                    "video_title": video.title,
                    "quiz": video.quiz_data,
                    "summary": video.summary
                }))
            else:
                await self.send(json.dumps({
                    "type": "error", 
                    "message": "Quiz for this video is not ready yet"
                }))
                
        except Video.DoesNotExist:
            await self.send(json.dumps({
                "type": "error", 
                "message": "Video not found"
            }))

    async def submit_answer(self, data):
        """Process user's answer to a quiz question"""
        video_id = data.get("video_id")
        question_index = data.get("question_index")
        selected_option = data.get("selected_option")
        
        try:
            from main.models import Video
            video = await sync_to_async(Video.objects.get)(pk=video_id)
            
            if not video.quiz_data or "questions" not in video.quiz_data:
                await self.send(json.dumps({
                    "type": "error",
                    "message": "Quiz not found"
                }))
                return
                
            questions = video.quiz_data["questions"]
            if question_index >= len(questions):
                await self.send(json.dumps({
                    "type": "error",
                    "message": "Question not found"
                }))
                return
                
            question = questions[question_index]
            correct_answer = None
            
            # Find the correct answer
            for i, option in enumerate(question["options"]):
                if option.get("correct", False):
                    correct_answer = i
                    break
            
            is_correct = selected_option == correct_answer
            
            await self.send(json.dumps({
                "type": "answer_result",
                "video_id": video_id,
                "question_index": question_index,
                "is_correct": is_correct,
                "correct_answer": correct_answer,
                "explanation": question["options"][correct_answer]["text"] if correct_answer is not None else ""
            }))
            
        except Video.DoesNotExist:
            await self.send(json.dumps({
                "type": "error",
                "message": "Video not found"
            }))