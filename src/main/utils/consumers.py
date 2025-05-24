import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from fetch_playlist import fetch_playlist_videos, fetch_transcript, get_playlist_title
from main.gemini_summarizer import summarize_with_chatgpt

class PlaylistConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        from main.models import Playlist, Video

        data = json.loads(text_data)
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
            transcript = await sync_to_async(fetch_transcript)(video_data["id"])
            summary = await sync_to_async(summarize_with_chatgpt)(transcript[:50000])

            # Update the video with transcript and summary
            video_obj.transcript = transcript
            video_obj.summary = summary
            await sync_to_async(video_obj.save)()

            # Send the new video to the client
            await self.send(json.dumps({
                "type": "video",
                "id": str(video_obj.id),
                "title": video_obj.title,
                "thumbnail": video_obj.thumbnail,
            }))
            
        # Notify that processing is complete
        await self.send(json.dumps({"type": "processing_complete"}))