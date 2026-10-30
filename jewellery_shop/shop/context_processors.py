from django.db.models import Sum
from .models import Wishlist, CartItem
from .roles import get_role, ROLE_ADMIN, ROLE_CUSTOMER


def user_role(request):
    """
    Makes the visitor's role available in every template:

        {{ user_role }}          "admin" / "customer" / "anonymous"
        {% if is_admin_user %}   true for admins
        {% if is_customer_user %} true for logged-in customers
    """

    role = get_role(request.user)

    wishlist_count = 0
    cart_count = 0
    if role == ROLE_CUSTOMER:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart_count = CartItem.objects.filter(cart__user=request.user).aggregate(
            total=Sum("quantity")
        )["total"] or 0

    return {
        "user_role": role,
        "wishlist_count": wishlist_count,
        "cart_count": cart_count,
        "is_admin_user": role == ROLE_ADMIN,
        "is_customer_user": role == ROLE_CUSTOMER,
    }
