from django.core.management.base import BaseCommand
from main.models import Video, Playlist


class Command(BaseCommand):
    help = 'Update order field for existing videos based on their creation order'

    def handle(self, *args, **options):
        playlists = Playlist.objects.all()
        
        for playlist in playlists:
            self.stdout.write(f'Updating video order for playlist: {playlist.title or playlist.url}')
            
            # Get videos ordered by creation time (id)
            videos = Video.objects.filter(playlist=playlist).order_by('id')
            
            for index, video in enumerate(videos):
                video.order = index
                video.save()
                self.stdout.write(f'  - Set order {index} for: {video.title}')
        
        self.stdout.write(self.style.SUCCESS('Successfully updated video order for all playlists!')) 