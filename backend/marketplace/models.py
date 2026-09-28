from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True, help_text="Tell the circular fashion community about yourself")
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    sustainability_points = models.PositiveIntegerField(default=120)
    eco_level = models.CharField(max_length=50, default='Eco Pioneer')

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Listing(models.Model):
    CATEGORY_CHOICES = [
        ('women', 'Women'),
        ('men', 'Men'),
        ('kids', 'Kids'),
        ('unisex', 'Unisex'),
        ('accessories', 'Accessories'),
        ('vintage', 'Vintage & Rare'),
    ]

    LISTING_TYPE_CHOICES = [
        ('sell', 'Buy / Sell'),
        ('rent', 'Rent'),
        ('resell', 'Resell'),
        ('swap', 'Swap'),
    ]

    CONDITION_CHOICES = [
        ('brand_new', 'Brand New with Tags'),
        ('like_new', 'Like New / Excellent'),
        ('gently_used', 'Gently Used / Good'),
        ('upcycled', 'Fair / Upcycled'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='women')
    title = models.CharField(max_length=255)
    description = models.TextField()
    brand = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50)
    condition = models.CharField(max_length=30, choices=CONDITION_CHOICES, default='like_new')
    condition_details = models.TextField(blank=True, help_text="Detailed note on wear, fabric care, dry-cleaned status")
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, default='sell')
    
    # Pricing
    sale_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    original_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    rental_price_per_day = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    security_deposit = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    swap_preferences = models.CharField(max_length=255, blank=True, help_text="What items seller wants in exchange")
    
    # Legacy cover image or primary image fallback
    image = models.ImageField(upload_to='listings/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    
    # AI Eco Impact Metrics
    co2_saved_kg = models.DecimalField(decimal_places=2, max_digits=6, default=6.20)
    water_saved_liters = models.DecimalField(decimal_places=2, max_digits=8, default=2700.00)
    waste_diverted_g = models.DecimalField(decimal_places=2, max_digits=8, default=450.00)
    sustainability_grade = models.CharField(max_length=5, default='A+')
    
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def primary_image_url(self):
        first_img = self.images.first()
        if first_img and first_img.image:
            return first_img.image.url
        if self.image:
            return self.image.url
        return None

    @property
    def all_images(self):
        imgs = list(self.images.all())
        if not imgs and self.image:
            return [self.image]
        return [item.image for item in imgs]


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listings/gallery/')
    caption = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.listing.title}"


class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    alternate_phone = models.CharField(max_length=15, blank=True)
    house_address = models.TextField()
    landmark = models.CharField(max_length=255, blank=True)
    pincode = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.full_name} - {self.city}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=Listing.LISTING_TYPE_CHOICES, default='sell')
    rental_days = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.listing.title}"

    @property
    def calculated_price(self):
        if self.transaction_type == 'rent':
            day_rate = self.listing.rental_price_per_day or 0
            deposit = self.listing.security_deposit or 0
            return (day_rate * self.rental_days) + deposit
        elif self.transaction_type == 'swap':
            return 0.00
        else:
            return self.listing.sale_price or 0.00


class Order(models.Model):
    STATUS_CHOICES = [
        ('placed', 'Order Placed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=Listing.LISTING_TYPE_CHOICES, default='sell')
    address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"