import os
import sys
import django
from decimal import Decimal
from PIL import Image, ImageDraw

# Force UTF-8 stdout on Windows
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from marketplace.models import UserProfile, Listing, ListingImage

def create_sample_image(filename, text, bg_color, text_color=(255, 255, 255)):
    media_dir = os.path.join(os.path.dirname(__file__), '..', 'media', 'listings')
    os.makedirs(media_dir, exist_ok=True)
    filepath = os.path.join(media_dir, filename)
    
    img = Image.new('RGB', (600, 750), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([30, 30, 570, 720], outline=(255, 255, 255), width=3)
    draw.text((60, 350), text, fill=text_color)
    
    img.save(filepath, 'JPEG')
    return f"listings/{filename}"

def seed():
    print("Seeding ReWear Circular Marketplace...")

    # Create Demo Users
    user1, _ = User.objects.get_or_create(username='sophia_eco', defaults={
        'email': 'sophia@rewear.org',
        'first_name': 'Sophia',
        'last_name': 'Chen'
    })
    user1.set_password('password123')
    user1.save()
    p1, _ = UserProfile.objects.get_or_create(user=user1, defaults={
        'bio': 'Passionate about circular fashion & vintage denim styling.',
        'sustainability_points': 340,
        'eco_level': 'Eco Legend'
    })

    user2, _ = User.objects.get_or_create(username='marcus_thrift', defaults={
        'email': 'marcus@rewear.org',
        'first_name': 'Marcus',
        'last_name': 'Vance'
    })
    user2.set_password('password123')
    user2.save()
    p2, _ = UserProfile.objects.get_or_create(user=user2, defaults={
        'bio': 'Curator of 90s streetwear and rare jackets.',
        'sustainability_points': 210,
        'eco_level': 'Eco Master'
    })

    # Sample Garment Listings
    items = [
        {
            'seller': user1,
            'title': 'Vintage Levi 501 Classic Blue Denim Jacket',
            'category': 'vintage',
            'listing_type': 'sell',
            'brand': "Levi's",
            'size': 'M',
            'condition': 'like_new',
            'condition_details': 'Perfect 90s wash, 100% heavy cotton. Dry-cleaned.',
            'description': 'Iconic authentic 90s Levis denim jacket. Timeless piece that gets better with age. Ideal for layering.',
            'sale_price': Decimal('2499.00'),
            'original_price': Decimal('6500.00'),
            'co2_saved_kg': Decimal('11.80'),
            'water_saved_liters': Decimal('5200.00'),
            'waste_diverted_g': Decimal('850.00'),
            'sustainability_grade': 'A+',
            'bg': (30, 80, 160),
            'text': "Levi's Vintage Denim",
        },
        {
            'seller': user2,
            'title': 'Designer Emerald Velvet Evening Gown',
            'category': 'women',
            'listing_type': 'rent',
            'brand': 'Sabyasachi / Designer',
            'size': 'S',
            'condition': 'brand_new',
            'condition_details': 'Worn once for photoshoot. Professionally sanitized.',
            'description': 'Stunning emerald green velvet dress with subtle embroidery. Perfect for galas, weddings, and formal occasions.',
            'rental_price_per_day': Decimal('850.00'),
            'security_deposit': Decimal('2000.00'),
            'co2_saved_kg': Decimal('8.50'),
            'water_saved_liters': Decimal('3400.00'),
            'waste_diverted_g': Decimal('500.00'),
            'sustainability_grade': 'A+',
            'bg': (5, 120, 85),
            'text': 'Emerald Velvet Gown',
        },
        {
            'seller': user1,
            'title': 'Oversized Beige Trench Coat',
            'category': 'unisex',
            'listing_type': 'swap',
            'brand': 'Zara Studio',
            'size': 'L',
            'condition': 'gently_used',
            'swap_preferences': 'Looking for size M leather jacket or wool blazer',
            'description': 'Classic beige minimalist trench coat with tortoiseshell buttons and tie belt. Great casual chic silhouette.',
            'co2_saved_kg': Decimal('7.20'),
            'water_saved_liters': Decimal('3100.00'),
            'waste_diverted_g': Decimal('620.00'),
            'sustainability_grade': 'A',
            'bg': (210, 180, 140),
            'text': 'Oversized Trench Coat',
        },
        {
            'seller': user2,
            'title': 'Nike Retro Windbreaker Track Jacket',
            'category': 'men',
            'listing_type': 'resell',
            'brand': 'Nike Retro',
            'size': 'L',
            'condition': 'like_new',
            'description': 'Color-blocked vintage Nike windbreaker. Lightweight waterproof fabric with mesh lining.',
            'sale_price': Decimal('1799.00'),
            'original_price': Decimal('4200.00'),
            'co2_saved_kg': Decimal('5.90'),
            'water_saved_liters': Decimal('2600.00'),
            'waste_diverted_g': Decimal('390.00'),
            'sustainability_grade': 'A',
            'bg': (40, 40, 50),
            'text': 'Nike Windbreaker',
        }
    ]

    for idx, item in enumerate(items):
        bg = item.pop('bg')
        txt = item.pop('text')
        img_rel_path = create_sample_image(f"sample_{idx+1}.jpg", txt, bg)
        
        listing, created = Listing.objects.get_or_create(
            title=item['title'],
            defaults={**item, 'image': img_rel_path}
        )
        if created:
            print(f"  + Created listing: {listing.title}")

    print("Seeding completed successfully!")

if __name__ == '__main__':
    seed()
