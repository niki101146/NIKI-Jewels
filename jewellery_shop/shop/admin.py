from django.contrib import admin
from .models import Category, Product, Wishlist, Cart, CartItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "is_available",
        "is_featured",
        "is_new_arrival",
        "created_at",
    )

    list_filter = (
        "category",
        "is_available",
        "is_featured",
        "is_new_arrival",
    )

    search_fields = (
        "name",
        "description",
    )

    list_editable = (
        "price",
        "stock",
        "is_available",
        "is_featured",
        "is_new_arrival", 
    )

    ordering = ("-created_at",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "added_at")

    search_fields = (
        "user__username",
        "product__name",
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "created_at",
    )

    search_fields = (
        "user__username",
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "product",
        "quantity",
        "created_at",
    )

    search_fields = (
        "product__name",
        "cart__user__username",
    )


