from django.core.management.base import BaseCommand
from django.core.management import call_command
from bars.models import Bar, BarPhoto, BarComment
import json
import os

class Command(BaseCommand):
    help = 'Export all bar data to JSON for Railway sync'
    
    def handle(self, *args, **options):
        # Export all data to JSON
        self.stdout.write('Exporting data to fixtures...')
        
        # Create fixtures directory
        os.makedirs('fixtures', exist_ok=True)
        
        # Export bars
        call_command('dumpdata', 'bars.Bar', '--output=fixtures/bars.json', '--indent=2')
        self.stdout.write(self.style.SUCCESS('✓ Exported bars'))
        
        # Export photos
        call_command('dumpdata', 'bars.BarPhoto', '--output=fixtures/photos.json', '--indent=2')
        self.stdout.write(self.style.SUCCESS('✓ Exported photos'))
        
        # Export comments
        call_command('dumpdata', 'bars.BarComment', '--output=fixtures/comments.json', '--indent=2')
        self.stdout.write(self.style.SUCCESS('✓ Exported comments'))
        
        # Export users and profiles
        call_command('dumpdata', 'auth.User', 'bars.UserProfile', '--output=fixtures/users.json', '--indent=2')
        self.stdout.write(self.style.SUCCESS('✓ Exported users'))
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Data exported to fixtures/ directory!\n'
                'Next steps:\n'
                '1. Commit fixtures to git\n'
                '2. Deploy to Railway\n'
                '3. Run: railway run python manage.py loaddata fixtures/*.json\n'
                '4. Sync data/ directory using Railway CLI'
            )
        )