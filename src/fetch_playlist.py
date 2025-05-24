import os
import time
from typing import List, Dict, Optional
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)
import yt_dlp
from dotenv import load_dotenv  
load_dotenv()
from main.gemini_summarizer import summarize_with_chatgpt
from main.summarize import summarize_with_gemini_1_5


# ---------- 1. Data-layer -------------------------------------------------
def fetch_playlist_videos(playlist_url: str) -> List[Dict[str, str]]:
    opts = {"quiet": True, "extract_flat": True, "skip_download": True, "forcejson": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        pl = ydl.extract_info(playlist_url, download=False)

    return [
        {"id": v["id"], 
         "title": v["title"], 
         "url": f"https://www.youtube.com/watch?v={v['id']}",
         "thumbnail": f"https://img.youtube.com/vi/{v['id']}/hqdefault.jpg",
        }
        for v in pl.get("entries", [])
    ]


def fetch_transcript(video_id: str) -> Optional[str]:
    """Вернуть транскрипт видео (или None, если недоступен)."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(chunk["text"] for chunk in transcript)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e: 
        return f"[Ошибка получения субтитров: {e}]"



def print_video_list(videos: List[Dict[str, str]]) -> None:
    print("\n=== Видео в плейлисте ===")
    for i, v in enumerate(videos, 1):
        print(f"{i}. {v['title']} — {v['url']}")


def print_transcripts(videos: List[Dict[str, str]]) -> None:
    """Для каждого видео сразу печатает транскрипт (или причину отсутствия)."""
    for i, v in enumerate(videos, 1):
        print(f"\n\n------ Транскрипт #{i}: {v['title']} ------")
        txt = fetch_transcript(v["id"])
        if txt is None:
            print("[Транскрипт недоступен]")
        elif txt.startswith("[Ошибка"):
            print(txt)
        else:
            print(txt)
            res =  summarize_with_chatgpt(txt)
            print(res)


def get_playlist_title(playlist_url):
    """Fetch the title of a YouTube playlist"""
    try:
        import pytube
        playlist = pytube.Playlist(playlist_url)
        return playlist.title
    except Exception as e:
        print(f"Error fetching playlist title: {e}")
        return None


# ---------- 3. Application-layer ----------------------------------------
def main() -> None:
    playlist = "https://youtube.com/playlist?list=PLhQjrBD2T3817j24-GogXmWqO5Q5vYy0V&si=MgpC8bn4FVv4-gOp"

    videos = fetch_playlist_videos(playlist)
    print_video_list(videos)
    print_transcripts(videos)


if __name__ == "__main__":
    main()
