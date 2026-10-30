from django.urls import path
from . import views
from .banner_urls import urlpatterns as banner_urlpatterns
from .password_urls import urlpatterns as password_urlpatterns

urlpatterns = [
    path("admin-dashboard/orders/", views.admin_orders, name="admin_orders"),
    path("orders/<int:order_id>/cancel/", views.cancel_customer_order, name="cancel_customer_order"),
    path("checkout/customer/", views.checkout_customer, name="checkout_customer"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    

    # ========================================================
    # HOME
    # ========================================================

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "collections/",
        views.collections,
        name="collections"
    ),


    # ========================================================
    # LOGIN + REGISTER (one page each) - role decides where you land
    # ========================================================

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "register/",
        views.register_view,
        name="register"
    ),


    # ========================================================
    # CUSTOMER
    # ========================================================

    path(
        "account/",
        views.account,
        name="account"
    ),

    path(
        "profile/", 
        views.profile, 
        name="profile"
    ),

    path(
        "orders/",
        views.orders,
        name="orders"
    ),

    path(
        "logout/",
        views.user_logout,
        name="user_logout"
    ),


    # ========================================================
    # WISHLIST
    # ========================================================

    path(
        "wishlist/",
        views.wishlist,
        name="wishlist"
    ),

    path(
        "wishlist/add/<int:product_id>/",
        views.add_to_wishlist,
        name="add_to_wishlist"
    ),

    path(
        "wishlist/remove/<int:product_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist"
    ),




    # ========================================================
    # CART
    # ========================================================

    path(
        "cart/",
        views.cart,
        name="cart"
    ),

    path(
        "cart/add/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/remove/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    path(
        "cart/update/<int:item_id>/",
        views.update_cart,
        name="update_cart"
    ),


    path(
        "admin-logout/",
        views.admin_logout,
        name="admin_logout"
    ),

    # =========================
    # ADMIN DASHBOARD
    # =========================

    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),


    # =========================
    # PRODUCT
    # =========================

    path(
        "admin-dashboard/product/add/",
        views.add_product,
        name="add_product"
    ),

    path(
        "admin-dashboard/product/edit/<int:product_id>/",
        views.edit_product,
        name="edit_product"
    ),

    path(
        "admin-dashboard/product/delete/<int:product_id>/",
        views.delete_product,
        name="delete_product"
    ),

    # ========================================================
    # OTHER PAGES
    # ========================================================

    path(
        "about/",
        views.about,
        name="about"
    ),

    path(
        "contact/",
        views.contact,
        name="contact"
    ),

]
urlpatterns += banner_urlpatterns
urlpatterns += password_urlpatterns