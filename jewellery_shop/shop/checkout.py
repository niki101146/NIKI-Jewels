from decimal import Decimal
from django.db import transaction
from django.db.models import F
from .models import Cart, CartItem, Product, Order, OrderItem


def place_order(user, details, number):
    with transaction.atomic():
        existing = Order.objects.filter(user=user, order_number=number).first()
        if existing:
            return existing
        carts = list(Cart.objects.select_for_update().filter(user=user))
        items = list(CartItem.objects.select_for_update().filter(cart__in=carts).select_related("product"))
        if not items:
            raise ValueError("Your cart is empty.")
        total = Decimal("0")
        for item in items:
            if item.quantity < 1 or not Product.objects.filter(pk=item.product_id, is_available=True, stock__gte=item.quantity).update(stock=F("stock") - item.quantity):
                raise ValueError(f"{item.product.name} does not have enough stock. Please update your cart.")
            total += item.product.price * item.quantity
        if total > Decimal("9999999999.99"):
            raise ValueError("This order is too large. Please contact the store.")
        address = "\n".join(filter(None, [details["name"], details["mobile"], details["email"], details["address"], details.get("landmark")]))
        order = Order.objects.create(user=user, order_number=number, total_amount=total,
            status="pending", shipping_address=address, city=details["city"],
            state=details["state"], pincode=details["pincode"], country="India")
        OrderItem.objects.bulk_create([OrderItem(order=order, product=i.product,
            product_name=i.product.name, price=i.product.price, quantity=i.quantity) for i in items])
        CartItem.objects.filter(pk__in=[i.pk for i in items]).delete()
        return order


def cancel_order(user, order_id):
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order_id, user=user)
        # Conditional transition also prevents repeated cancellation restoring stock twice.
        changed = Order.objects.filter(pk=order.pk, status="pending").update(status="cancelled")
        if changed:
            for item in order.items.all():
                if item.product_id:
                    Product.objects.filter(pk=item.product_id).update(stock=F("stock") + item.quantity)
        return bool(changed)
