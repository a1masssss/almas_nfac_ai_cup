from django.core.management.base import BaseCommand
from main.models import Video
import json


class Command(BaseCommand):
    help = 'Fix quiz data format issues'

    def handle(self, *args, **options):
        videos = Video.objects.filter(quiz_data__isnull=False)
        self.stdout.write(f'Found {videos.count()} videos with quiz data')
        
        fixed_count = 0
        for video in videos:
            try:
                # Check if quiz_data is a string that needs parsing
                if isinstance(video.quiz_data, str):
                    self.stdout.write(f'Fixing quiz data for: {video.title}')
                    parsed_data = json.loads(video.quiz_data)
                    video.quiz_data = parsed_data
                    video.save()
                    fixed_count += 1
                else:
                    # Validate existing JSON structure
                    if isinstance(video.quiz_data, dict) and 'questions' in video.quiz_data:
                        self.stdout.write(f'Quiz data OK for: {video.title}')
                    else:
                        self.stdout.write(f'Invalid quiz data structure for: {video.title}')
                        
            except json.JSONDecodeError as e:
                self.stdout.write(f'Error parsing quiz data for {video.title}: {e}')
            except Exception as e:
                self.stdout.write(f'Unexpected error for {video.title}: {e}')
        
        self.stdout.write(f'Fixed {fixed_count} videos')
        self.stdout.write(self.style.SUCCESS('Quiz data fix completed!')) 