import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from .models import Listing, ListingImage, CartItem, Order, DeliveryAddress, UserProfile
from .forms import SignUpForm, ListingForm, DeliveryAddressForm, UserProfileForm


def calculate_ai_eco_metrics(category, condition, sale_price=None, original_price=None):
    """
    AI Circular Fashion Impact Engine
    Calculates CO2 savings, water saved, waste diverted, and sustainability rating based on garment metrics.
    """
    category = (category or 'women').lower()
    
    # Base CO2 (kg) & Water (Liters) multiplier per category
    metrics = {
        'women': {'co2': 6.5, 'water': 2700, 'waste': 420},
        'men': {'co2': 7.2, 'water': 3100, 'waste': 480},
        'kids': {'co2': 3.5, 'water': 1400, 'waste': 210},
        'unisex': {'co2': 6.0, 'water': 2600, 'waste': 400},
        'accessories': {'co2': 2.8, 'water': 900, 'waste': 180},
        'vintage': {'co2': 12.0, 'water': 5200, 'waste': 850},
    }
    
    base = metrics.get(category, {'co2': 5.5, 'water': 2500, 'waste': 400})
    
    # Condition multiplier
    cond_factor = {
        'brand_new': 0.9,
        'like_new': 1.1,
        'gently_used': 1.25,
        'upcycled': 1.4,
    }.get(condition, 1.0)
    
    co2 = round(base['co2'] * cond_factor, 2)
    water = round(base['water'] * cond_factor, 2)
    waste = round(base['waste'] * cond_factor, 2)
    
    # Grade assignment
    if co2 > 8.0 or category == 'vintage':
        grade = 'A+'
    elif co2 > 5.0:
        grade = 'A'
    else:
        grade = 'B+'
        
    return {
        'co2_saved_kg': Decimal(str(co2)),
        'water_saved_liters': Decimal(str(water)),
        'waste_diverted_g': Decimal(str(waste)),
        'sustainability_grade': grade,
    }


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure UserProfile exists
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f"Welcome to ReWear, {user.first_name or user.username}! Your profile is ready.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


def home_view(request):
    listings = Listing.objects.filter(is_available=True).order_by('-created_at')[:8]
    
    # Global Sustainability Community Impact
    impact_stats = Listing.objects.aggregate(
        total_co2=Sum('co2_saved_kg'),
        total_water=Sum('water_saved_liters'),
        total_waste=Sum('waste_diverted_g')
    )
    
    co2_total = round(float(impact_stats['total_co2'] or 124.50), 1)
    water_total = round(float(impact_stats['total_water'] or 48200.00), 0)
    waste_total = round(float(impact_stats['total_waste'] or 8900.00) / 1000.0, 1) # in kg

    return render(request, 'marketplace/home.html', {
        'listings': listings,
        'co2_total': co2_total,
        'water_total': water_total,
        'waste_total': waste_total,
    })


def catalog_view(request):
    listings = Listing.objects.all().order_by('-created_at')
    
    # Filters
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    listing_type = request.GET.get('type', '').strip()
    condition = request.GET.get('condition', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    if q:
        listings = listings.filter(
            Q(title__icontains=q) | 
            Q(description__icontains=q) | 
            Q(brand__icontains=q)
        )
    if category:
        listings = listings.filter(category=category)
    if listing_type:
        listings = listings.filter(listing_type=listing_type)
    if condition:
        listings = listings.filter(condition=condition)
    if min_price:
        try:
            listings = listings.filter(sale_price__gte=Decimal(min_price))
        except Exception:
            pass
    if max_price:
        try:
            listings = listings.filter(sale_price__lte=Decimal(max_price))
        except Exception:
            pass

    return render(request, 'marketplace/catalog.html', {
        'listings': listings,
        'search_query': q,
        'selected_category': category,
        'selected_type': listing_type,
        'selected_condition': condition,
        'categories': Listing.CATEGORY_CHOICES,
        'listing_types': Listing.LISTING_TYPE_CHOICES,
        'conditions': Listing.CONDITION_CHOICES,
    })


def listing_detail_view(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    
    # Track view count
    listing.views_count += 1
    listing.save(update_fields=['views_count'])

    # Similar circular listings
    related_items = Listing.objects.filter(category=listing.category, is_available=True).exclude(id=listing.id)[:4]

    # Seller details
    seller_profile, _ = UserProfile.objects.get_or_create(user=listing.seller)

    return render(request, 'marketplace/listing_detail.html', {
        'listing': listing,
        'related_items': related_items,
        'seller_profile': seller_profile,
    })


@login_required
def add_listing_view(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            
            # Run AI Eco Calculator
            eco_metrics = calculate_ai_eco_metrics(
                listing.category, 
                listing.condition, 
                listing.sale_price, 
                listing.original_price
            )
            listing.co2_saved_kg = eco_metrics['co2_saved_kg']
            listing.water_saved_liters = eco_metrics['water_saved_liters']
            listing.waste_diverted_g = eco_metrics['waste_diverted_g']
            listing.sustainability_grade = eco_metrics['sustainability_grade']
            
            listing.save()

            # Process multiple uploaded images
            extra_images = request.FILES.getlist('extra_images')
            for idx, img_file in enumerate(extra_images):
                ListingImage.objects.create(listing=listing, image=img_file)
                if idx == 0 and not listing.image:
                    listing.image = img_file
                    listing.save(update_fields=['image'])

            # Reward seller eco-points
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.sustainability_points += 50
            profile.save()

            messages.success(request, f"🎉 Listing '{listing.title}' published! You earned +50 Eco Points.")
            return redirect('listing_detail', listing_id=listing.id)
        else:
            messages.error(request, "Please fix the errors in your listing details.")
    else:
        form = ListingForm()

    return render(request, 'marketplace/add_listing.html', {'form': form})


def ai_tag_assistant_api(request):
    """API Endpoint for AI Smart Tagging and Pricing Assistance"""
    category = request.GET.get('category', 'women')
    condition = request.GET.get('condition', 'like_new')
    brand = request.GET.get('brand', '')
    
    eco = calculate_ai_eco_metrics(category, condition)
    
    res = {
        'co2_saved': str(eco['co2_saved_kg']),
        'water_saved': str(eco['water_saved_liters']),
        'waste_diverted': str(eco['waste_diverted_g']),
        'grade': eco['sustainability_grade'],
        'smart_tip': f"Items from {brand or 'sustainable brands'} in {condition.replace('_', ' ')} condition save over {eco['co2_saved_kg']}kg CO2!"
    }
    return JsonResponse(res)


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
    user_orders = Order.objects.filter(buyer=request.user).order_by('-ordered_at')
    
    total_co2 = user_listings.aggregate(Sum('co2_saved_kg'))['co2_saved_kg__sum'] or 0.0

    return render(request, 'marketplace/profile.html', {
        'profile': profile,
        'listings': user_listings,
        'orders': user_orders,
        'total_co2': round(total_co2, 1),
    })


@login_required
def edit_profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'marketplace/edit_profile.html', {'form': form})


@login_required
def seller_dashboard_view(request):
    my_listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
    active_count = my_listings.filter(is_available=True).count()
    sold_count = my_listings.filter(is_available=False).count()
    
    return render(request, 'marketplace/seller_dashboard.html', {
        'listings': my_listings,
        'active_count': active_count,
        'sold_count': sold_count,
    })


@login_required
def add_to_cart_view(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    
    if not listing.is_available:
        messages.error(request, "Sorry, this piece is no longer available.")
        return redirect('home')

    if listing.seller == request.user:
        messages.error(request, "You cannot add your own item to your cart.")
        return redirect('listing_detail', listing_id=listing.id)
        
    ttype = request.GET.get('type', listing.listing_type)
    CartItem.objects.get_or_create(
        user=request.user, 
        listing=listing, 
        defaults={'transaction_type': ttype}
    )
    messages.success(request, f"Added '{listing.title}' to your circular cart!")
    return redirect('cart_view')


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_amount = sum(item.calculated_price for item in cart_items if item.listing.is_available)
    co2_saved = sum(item.listing.co2_saved_kg for item in cart_items if item.listing.is_available)

    return render(request, 'marketplace/cart.html', {
        'cart_items': cart_items, 
        'total': total_amount,
        'co2_saved': round(co2_saved, 1),
    })


@login_required
def remove_from_cart_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    title = cart_item.listing.title
    cart_item.delete()
    messages.info(request, f"Removed '{title}' from cart.")
    return redirect('cart_view')


@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.warning(request, "Your cart is currently empty.")
        return redirect('catalog')

    # Pre-fill address if profile exists
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    initial_data = {
        'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
        'phone': profile.phone,
        'email': request.user.email,
        'house_address': profile.address,
        'city': profile.city,
        'state': profile.state,
        'pincode': profile.pincode,
    }

    if request.method == 'POST':
        address_form = DeliveryAddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()

            orders_created = []
            for item in cart_items:
                listing = item.listing
                if listing.is_available:
                    price = item.calculated_price
                    order = Order.objects.create(
                        buyer=request.user,
                        listing=listing,
                        transaction_type=item.transaction_type,
                        address=address,
                        total_price=price,
                        status='placed'
                    )
                    orders_created.append(order)
                    
                    # Mark item as sold / rented out
                    listing.is_available = False
                    listing.save(update_fields=['is_available'])

            cart_items.delete()  # Clear cart
            
            # Award buyer Eco Points
            profile.sustainability_points += (len(orders_created) * 100)
            profile.save()

            messages.success(request, "♻️ Order placed successfully! Thank you for choosing circular fashion.")
            return redirect('order_success')
    else:
        address_form = DeliveryAddressForm(initial=initial_data)

    total_amount = sum(item.calculated_price for item in cart_items if item.listing.is_available)
    co2_total = sum(item.listing.co2_saved_kg for item in cart_items if item.listing.is_available)

    return render(request, 'marketplace/checkout.html', {
        'cart_items': cart_items, 
        'address_form': address_form,
        'total': total_amount,
        'co2_total': round(co2_total, 1),
    })


@login_required
def order_success_view(request):
    latest_orders = Order.objects.filter(buyer=request.user).order_by('-ordered_at')[:4]
    return render(request, 'marketplace/order_success.html', {'orders': latest_orders})