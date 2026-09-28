from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('listing/<int:listing_id>/', views.listing_detail_view, name='listing_detail'),
    path('add-listing/', views.add_listing_view, name='add_listing'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('seller-dashboard/', views.seller_dashboard_view, name='seller_dashboard'),
    
    # Cart & Checkout
    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:listing_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-success/', views.order_success_view, name='order_success'),

    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('register/', views.signup_view, name='register'), # alias for signup
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # AI API
    path('api/ai-tag-assistant/', views.ai_tag_assistant_api, name='ai_tag_assistant'),
]