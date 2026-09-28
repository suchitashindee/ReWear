from django.contrib import admin
from .models import UserProfile, Listing, ListingImage, DeliveryAddress, CartItem, Order


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'listing_type', 'condition', 'sale_price', 'rental_price_per_day', 'is_available', 'co2_saved_kg', 'created_at')
    list_filter = ('category', 'listing_type', 'condition', 'is_available')
    search_fields = ('title', 'description', 'brand', 'seller__username')
    inlines = [ListingImageInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'sustainability_points', 'eco_level')
    search_fields = ('user__username', 'user__email', 'city', 'phone')


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'phone', 'city', 'state', 'pincode')
    search_fields = ('full_name', 'city', 'pincode', 'phone')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'listing', 'transaction_type', 'total_price', 'status', 'ordered_at')
    list_filter = ('transaction_type', 'status')
    search_fields = ('buyer__username', 'listing__title')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'transaction_type', 'added_at')