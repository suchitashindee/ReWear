from .models import CartItem, UserProfile

def cart_context(request):
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return {
            'cart_count': count,
            'user_profile': profile,
        }
    return {
        'cart_count': 0,
        'user_profile': None,
    }
