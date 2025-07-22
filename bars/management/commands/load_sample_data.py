from django.core.management.base import BaseCommand
from bars.models import Bar
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Load sample bar data for testing'

    def handle(self, *args, **options):
        # Clear existing data
        Bar.objects.all().delete()
        
        # Sample bars data
        bars_data = [
            {
                'name': 'Bar Nestor',
                'address': 'Kale Nagusia 11, 20003 Donostia-San Sebastián',
                'notes': 'Famous for their tortilla and txuleta. Always packed but worth the wait. Cash only!',
                'specialties': 'Tortilla de patatas, Txuleta',
                'price_range': '€€',
                'cana_price': 2.50,
                'crowd_level': 'crowded',
                'last_visited': date.today() - timedelta(days=2),
                'tags': 'traditional, tortilla, cash-only, famous',
                'map_link': 'https://maps.google.com/?q=Bar+Nestor+San+Sebastian'
            },
            {
                'name': 'La Cuchara de San Telmo',
                'address': 'Kale Nagusia 4, 20003 Donostia-San Sebastián',
                'notes': 'Creative pintxos with modern twists. The foie micuit is incredible. Great wine selection.',
                'specialties': 'Modern pintxos, Foie micuit, Wine',
                'price_range': '€€€',
                'cana_price': 3.00,
                'crowd_level': 'medium',
                'last_visited': date.today() - timedelta(days=5),
                'tags': 'modern, creative, wine, upscale',
                'map_link': 'https://maps.google.com/?q=La+Cuchara+San+Telmo'
            },
            {
                'name': 'Gandarias',
                'address': 'Kale Nagusia 23, 20003 Donostia-San Sebastián',  
                'notes': 'Traditional atmosphere with excellent jamón and cheese. Good value for money.',
                'specialties': 'Jamón ibérico, Manchego cheese, Traditional pintxos',
                'price_range': '€€',
                'cana_price': 2.20,
                'crowd_level': 'medium',
                'last_visited': date.today() - timedelta(days=1),
                'tags': 'traditional, jamon, cheese, good-value',
            },
            {
                'name': 'Atari',
                'address': 'Mayor 18, 20003 Donostia-San Sebastián',
                'notes': 'Hidden gem with amazing mushroom risotto pintxos. Quieter than most places in the old town.',
                'specialties': 'Mushroom risotto, Seasonal pintxos',
                'price_range': '€€',
                'cana_price': 2.80,
                'crowd_level': 'quiet',
                'last_visited': date.today() - timedelta(days=7),
                'tags': 'hidden-gem, mushrooms, seasonal, quiet',
            },
            {
                'name': 'Bar Martinez',
                'address': 'Kale Nagusia 13, 20003 Donostia-San Sebastián',
                'notes': 'Great for breakfast pintxos and coffee. Opens early, perfect for starting the day.',
                'specialties': 'Breakfast pintxos, Coffee',
                'price_range': '€',
                'cana_price': 1.80,
                'crowd_level': 'quiet',
                'last_visited': date.today() - timedelta(days=3),
                'tags': 'breakfast, coffee, early-opening, budget-friendly',
            }
        ]
        
        for bar_data in bars_data:
            bar = Bar.objects.create(**bar_data)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created bar: {bar.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully loaded {len(bars_data)} sample bars')
        )