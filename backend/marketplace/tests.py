from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from marketplace.models import Listing, CartItem, Order, UserProfile, DeliveryAddress
from marketplace.views import calculate_ai_eco_metrics


class MarketplaceTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@rewear.org',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.profile = UserProfile.objects.create(user=self.user)

        self.seller = User.objects.create_user(
            username='seller',
            email='seller@rewear.org',
            password='password123'
        )
        self.seller_profile = UserProfile.objects.create(user=self.seller)

        self.listing = Listing.objects.create(
            seller=self.seller,
            title='Sample Vintage Coat',
            category='women',
            listing_type='sell',
            brand='Zara',
            size='M',
            condition='like_new',
            description='A beautiful pre-loved coat.',
            sale_price=Decimal('1500.00'),
            co2_saved_kg=Decimal('6.50'),
            water_saved_liters=Decimal('2700.00'),
            waste_diverted_g=Decimal('420.00'),
            sustainability_grade='A'
        )

    def test_ai_eco_calculator(self):
        metrics = calculate_ai_eco_metrics('women', 'like_new')
        self.assertIn('co2_saved_kg', metrics)
        self.assertIn('water_saved_liters', metrics)
        self.assertGreater(metrics['co2_saved_kg'], 0)

    def test_home_and_catalog_views(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ReWear')

        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sample Vintage Coat')

    def test_listing_detail_view(self):
        response = self.client.get(reverse('listing_detail', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sample Vintage Coat')

    def test_cart_and_checkout_flow(self):
        self.client.login(username='testuser', password='password123')

        # Add to cart
        response = self.client.get(reverse('add_to_cart', args=[self.listing.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CartItem.objects.filter(user=self.user, listing=self.listing).exists())

        # View Cart
        response = self.client.get(reverse('cart_view'))
        self.assertEqual(response.status_code, 200)

        # Checkout
        checkout_data = {
            'full_name': 'Test User',
            'phone': '9876543210',
            'email': 'test@rewear.org',
            'house_address': '123 Circular Street',
            'pincode': '110001',
            'city': 'New Delhi',
            'state': 'Delhi'
        }
        response = self.client.post(reverse('checkout'), checkout_data)
        self.assertEqual(response.status_code, 302)

        # Verify Order created and listing marked unavailable
        self.assertTrue(Order.objects.filter(buyer=self.user, listing=self.listing).exists())
        self.listing.refresh_from_db()
        self.assertFalse(self.listing.is_available)
