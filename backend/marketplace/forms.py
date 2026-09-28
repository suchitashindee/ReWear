from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Listing, UserProfile, DeliveryAddress


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=50, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = (
            "title",
            "category",
            "listing_type",
            "brand",
            "size",
            "condition",
            "condition_details",
            "description",
            "sale_price",
            "original_price",
            "rental_price_per_day",
            "security_deposit",
            "swap_preferences",
            "image",
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Vintage Levi\'s Denim Jacket'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'listing_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_listing_type'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Zara, Nike, Thrifted'}),
            'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., M / UK 10 / EU 38'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'condition_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Mention dry cleaning, minor flaws, or fabric care...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe fit, material, style, and history of the piece...'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'original_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Original retail price'}),
            'rental_price_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Daily rate'}),
            'security_deposit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Refundable deposit'}),
            'swap_preferences': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Looking for Size S coats or Boho dresses'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("phone", "bio", "address", "city", "state", "pincode", "profile_image")
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your sustainable fashion journey...'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = (
            "full_name",
            "phone",
            "email",
            "alternate_phone",
            "house_address",
            "landmark",
            "pincode",
            "city",
            "state",
        )
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Receiver\'s Full Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional Alternate Number'}),
            'house_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Flat/House No., Building, Street'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nearby Landmark'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '6-digit Pincode'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
        }