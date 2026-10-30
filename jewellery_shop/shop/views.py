from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from urllib.parse import quote
from .models import ContactMessage
from django.conf import settings
from .models import Category, Product, Wishlist, Cart, CartItem, CustomerProfile
from .forms import  ProductForm
from .models import CustomerProfile
from .forms import UserProfileForm, CustomerProfileForm, RegisterForm
from .models import Product, Order, OrderItem
from .recommendations import recommend_for, record_view, similar_to, wishlist_ids
from .banner_models import HeroBanner, HomeCategory
from .roles import (
    admin_required,
    customer_required,
    get_next,
    home_url_for,
    is_admin_role,
    post_login_url,
)


# =========================
# HOME PAGE
# =========================

def home(request):

    featured_products = Product.objects.filter(
        is_available=True,
        is_featured=True
    )

    new_arrivals = Product.objects.filter(
        is_available=True,
        is_new_arrival=True
    ).order_by("-created_at")[:8]

    categories = Category.objects.all()

    # =========================
    # WISHLIST
    # =========================

    wishlist_product_ids = set()

    if request.user.is_authenticated:
        wishlist_product_ids = set(
            Wishlist.objects.filter(
                user=request.user
            ).values_list(
                "product_id",
                flat=True
            )
        )

    # Owner-managed content (Admin > Hero Banners / Categories). If the tables do not exist yet
    # (migration not run) the home page still works with its built-in banner and categories.
    try:
        hero_banners = list(HeroBanner.objects.filter(is_active=True))
        home_categories = list(HomeCategory.objects.filter(is_active=True))
    except Exception:
        hero_banners, home_categories = [], []

    return render(
        request,
        "shop/home.html",
        {
            "hero_banners": hero_banners,
            "home_categories": home_categories,
            "featured_products": featured_products,
            "new_arrivals": new_arrivals,
            "categories": categories,
            "wishlist_product_ids": wishlist_product_ids,
            "recommended_products": recommend_for(request, limit=8),
        }
    )


# =========================
# COLLECTIONS / SEARCH / FILTERS
# =========================

def collections(request):

    products = Product.objects.all().select_related("category")
    categories = Category.objects.all()

    # =========================
    # SEARCH
    # =========================

    query = request.GET.get("q", "").strip()

    if query:
        products = products.filter(name__istartswith=query)
    # =========================
    # GENDER FILTER
    # =========================

    selected_genders = request.GET.getlist("gender")

    if selected_genders:
        products = products.filter(
            gender__in=selected_genders
        )

    # =========================
    # MATERIAL FILTER
    # =========================

    selected_materials = request.GET.getlist("material")

    if selected_materials:
        products = products.filter(
            material__in=selected_materials
        )

    # =========================
    # CATEGORY FILTER
    # =========================
    selected_categories = request.GET.getlist("category")

    if selected_categories:
        products = products.filter(
            category_id__in=selected_categories
        )

    # =========================
    # WISHLIST
    # =========================

    wishlist_product_ids = set()

    if request.user.is_authenticated:
        wishlist_product_ids = set(
            Wishlist.objects.filter(
                user=request.user
            ).values_list(
                "product_id",
                flat=True
            )
        )

    # =========================
    # RENDER
    # =========================

    return render(
        request,
        "shop/collections.html",
        {
            "products": products,
            "categories": categories,
            "search_query": query,
            "selected_genders": selected_genders,
            "selected_materials": selected_materials,
            "selected_categories": selected_categories,
            "wishlist_product_ids": wishlist_product_ids,
        }
    )
# =========================
# WISHLIST
# =========================

@customer_required
def wishlist(request):

    wishlist_items = (
        Wishlist.objects
        .filter(user=request.user)
        .select_related("product", "product__category")
    )

    print("================================")
    print("WISHLIST PAGE TEST")
    print("Logged-in user:", request.user)
    print("User ID:", request.user.id)
    print("Wishlist count:", wishlist_items.count())

    for item in wishlist_items:
        print(
            "Wishlist:",
            item.id,
            "| Product:",
            item.product.name,
            "| Product ID:",
            item.product.id
        )

    print("================================")

    return render(
        request,
        "shop/wishlist.html",
        {
            "wishlist_items": wishlist_items,
        }
    )


@customer_required
def add_to_wishlist(request, product_id):

    if request.method != "POST":
        return redirect("home")

    product = get_object_or_404(
        Product,
        id=product_id
    )

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    print("================================")
    print("WISHLIST TEST")
    print("User:", request.user)
    print("Product:", product)
    print("Product ID:", product.id)
    print("Wishlist ID:", wishlist_item.id)
    print("Created:", created)
    print("================================")

    return redirect(
        request.META.get("HTTP_REFERER", "home") + "#new-arrivals"
    )


@customer_required
def remove_from_wishlist(request, product_id):

    if request.method != "POST":
        return redirect("home")

    Wishlist.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()

    return redirect(
        request.META.get("HTTP_REFERER", "home") + "#new-arrivals"
    )
# =========================
# CART
# =========================

@customer_required
def cart(request):

    try:
        cart = Cart.objects.get(
            user=request.user
        )

        cart_items = cart.items.select_related(
            "product"
        )

    except Cart.DoesNotExist:

        cart_items = []

    total = sum(
        item.total_price()
        for item in cart_items
    )

    return render(
        request,
        "shop/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
            "wishlist_product_ids": wishlist_ids(request),
        }
    )


@customer_required
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    # Get this customer's cart
    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    # Check whether product is already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    # If already exists, increase quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


@customer_required
def remove_from_cart(request, item_id):
    if request.method != "POST":
        return redirect("cart")

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    item.delete()

    return redirect("cart")


@customer_required
def update_cart(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if request.method == "POST":

        try:
            quantity = int(request.POST.get("quantity", 1))
        except (ValueError, TypeError):
            quantity = 1

        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()

    return redirect("cart")


# ============================================================
# CUSTOMER ACCOUNT
# ============================================================

@customer_required
def account(request):
    return render(
        request,
        "shop/account.html"
    )


# ============================================================
# CUSTOMER PROFILE
# ============================================================

@customer_required
def profile(request):

    customer_profile, created = CustomerProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "country": "India",
        }
    )

    if request.method == "POST":

        user_form = UserProfileForm(
            request.POST,
            instance=request.user
        )

        profile_form = CustomerProfileForm(
            request.POST,
            instance=customer_profile
        )

        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()
            profile_form.save()

            messages.success(
                request,
                "Your profile has been updated successfully."
            )

            return redirect("profile")

    else:

        user_form = UserProfileForm(
            instance=request.user
        )

        profile_form = CustomerProfileForm(
            instance=customer_profile
        )

    return render(
        request,
        "shop/profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "customer_profile": customer_profile,
        }
    )

# ============================================================
# CUSTOMER ORDERS
# ============================================================

@customer_required
def orders(request):

    customer_orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        "items"
    )

    return render(
        request,
        "shop/orders.html",
        {
            "orders": customer_orders,
        }
    )

# ==========================================
# LOGOUT (customers and admins)
# ==========================================

def user_logout(request):

    was_admin = is_admin_role(request.user)

    logout(request)

    # Admins go back to the login page, customers to the shop.
    if was_admin:
        return redirect("login")

    return redirect("home")


# Old name kept so existing links keep working.
admin_logout = user_logout


# =========================
# ABOUT / CONTACT
# =========================

def about(request):
    return render(request, "shop/about.html")


def contact(request):

    if request.method == "POST":

        # ==========================================
        # GET CUSTOMER DETAILS
        # ==========================================

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()

        # ==========================================
        # CHECK REQUIRED FIELDS
        # ==========================================

        if not name or not email or not message:

            messages.error(
                request,
                "Please fill in all required fields."
            )

            return render(
                request,
                "shop/contact.html"
            )

        # ==========================================
        # SAVE ENQUIRY TO DATABASE
        # ==========================================

        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        # ==========================================
        # SEND THE MESSAGE TO THE STORE (from the website)
        # ==========================================

        from django.core.mail import EmailMessage

        store_email = "nikildanniki@gmail.com"

        clean_name = " ".join(name.split())          # no line breaks in headers
        email_body = (
            "New message from the NIKI Jewels website contact form\n\n"
            f"Customer Name: {name}\n"
            f"Customer Email: {email}\n"
            f"Phone: {phone}\n\n"
            f"Message:\n{message}\n"
        )

        try:
            EmailMessage(
                subject=f"Contact from {clean_name}",
                body=email_body,
                from_email=None,                       # DEFAULT_FROM_EMAIL
                to=[store_email],
                reply_to=[email],                      # Reply goes to the customer
            ).send(fail_silently=False)
        except Exception as exc:
            print("Contact email failed:", exc)
            messages.error(
                request,
                "Sorry, your message could not be sent right now. "
                "Please try again or call us."
            )
            return redirect("contact")

        messages.success(
            request,
            "Thank you! Your message has been sent. We will get back to you soon."
        )

        return redirect("contact")

    return render(
        request,
        "shop/contact.html"
    )

# ==================================================
# LOGIN  (one page for everybody)
#
# Username + password. After login the user's ROLE decides
# where they land:
#     admin    -> admin dashboard
#     customer -> account page
# ==================================================

def login_view(request):

    # Already logged in -> go to the home page of their role
    if request.user.is_authenticated:
        return redirect(home_url_for(request.user))

    username = ""

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:

            messages.error(
                request,
                "Please enter your username and password."
            )

        else:

            # Find the account ignoring upper/lower case ("DrSmith" = "drsmith"),
            # and allow the e-mail address as the username too.
            account = User.objects.filter(username__iexact=username).first()
            if account is None and "@" in username:
                matches = User.objects.filter(email__iexact=username)
                account = matches.first() if matches.count() == 1 else None

            user = authenticate(
                request,
                username=account.username if account else username,
                password=password
            )

            if user is not None:

                login(request, user)

                return redirect(post_login_url(request, user))

            # Tell the customer when the password was right but the account is switched off.
            if account is not None and not account.is_active and account.check_password(password):
                messages.error(
                    request,
                    "This account is disabled. Please contact the store."
                )
            else:
                messages.error(
                    request,
                    "Invalid username or password."
                )

            # Reason for the store owner (visible in the server console only).
            if account is None:
                print(f"LOGIN FAILED: no user named '{username}'")
            elif not account.has_usable_password():
                print(f"LOGIN FAILED: '{account.username}' has no usable password - run: python manage.py changepassword {account.username}")
            elif "$" not in account.password:
                print(f"LOGIN FAILED: '{account.username}' password is stored as plain text, not hashed - run: python manage.py changepassword {account.username}")
            elif not account.is_active:
                print(f"LOGIN FAILED: '{account.username}' is inactive (is_active = False)")
            else:
                print(f"LOGIN FAILED: wrong password for '{account.username}'")

    return render(
        request,
        "shop/login.html",
        {
            "username": username,
            "next": get_next(request),
        }
    )


# ==================================================
# REGISTER  (customers only)
#
# Username, email, password, confirm password.
# Anyone who registers here becomes a CUSTOMER.
# Admin accounts are never created from this page.
# ==================================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect(home_url_for(request.user))

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
            )

            CustomerProfile.objects.get_or_create(user=user)

            login(request, user)

            messages.success(
                request,
                "Your account has been created. Welcome!"
            )

            return redirect(post_login_url(request, user))

    else:

        form = RegisterForm()

    return render(
        request,
        "shop/register.html",
        {
            "form": form,
            "next": get_next(request),
        }
    )


# =========================
# ADMIN DASHBOARD
# =========================

@admin_required
def admin_dashboard(request):
    from django.utils import timezone
    from zoneinfo import ZoneInfo
    from datetime import datetime, time, timedelta
    zone = ZoneInfo("Asia/Kolkata")
    start = datetime.combine(timezone.now().astimezone(zone).date(), time.min, tzinfo=zone)
    show_low_stock = request.GET.get("stock") == "low"
    products = Product.objects.select_related("category").all()
    if show_low_stock:
        products = products.filter(stock__lte=1).order_by("stock", "name")
    return render(request, "shop/admin/dashboard.html", {
        "admin_page": "dashboard",
        "total_orders": Order.objects.count(),
        "products": products,
        "show_low_stock": show_low_stock,
        "total_products": Product.objects.count(),
        "today_orders": Order.objects.filter(created_at__gte=start, created_at__lt=start + timedelta(days=1)).count(),
        "low_stock": Product.objects.filter(stock__lte=1).count(),
        "pending_orders": Order.objects.filter(status="pending").count(),
    })


@admin_required
def admin_orders(request):
    # Admin changes an order's status from the orders table.
    if request.method == "POST":
        valid = {value for value, _label in Order._meta.get_field("status").choices}
        order = get_object_or_404(Order, pk=request.POST.get("order_id"))
        new_status = request.POST.get("status", "")
        if new_status not in valid:
            messages.error(request, "Invalid status.")
        elif new_status == order.status:
            pass
        elif order.status == "cancelled":
            messages.error(request, f"Order {order.pk} is cancelled and cannot be reopened.")
        elif new_status == "cancelled":
            # use the shared cancel logic so stock is handled the same way as customer cancels
            from .checkout import cancel_order
            if cancel_order(order.user, order.pk):
                messages.success(request, f"Order {order.pk} cancelled.")
            else:
                messages.error(request, f"Order {order.pk} could not be cancelled here (only pending orders can be).")
        else:
            order.status = new_status
            order.save(update_fields=["status"])
            messages.success(request, f"Order {order.pk} marked as {order.get_status_display()}.")
        return redirect(request.get_full_path())

    from django.core.paginator import Paginator
    from django.db.models import Sum
    from django.utils import timezone
    from zoneinfo import ZoneInfo
    from datetime import datetime, time, timedelta
    from decimal import Decimal
    import re
    zone = ZoneInfo("Asia/Kolkata")
    today = timezone.now().astimezone(zone).date()
    start = datetime.combine(today, time.min, tzinfo=zone)
    daily = Order.objects.filter(created_at__gte=start, created_at__lt=start + timedelta(days=1))
    show_all = request.GET.get("orders") != "today"
    listing = Order.objects.all() if show_all else daily
    listing = listing.select_related("user", "user__customer_profile").prefetch_related("items__product").order_by("-created_at", "-pk")
    page = Paginator(listing, 20).get_page(request.GET.get("page"))
    for order in page:
        lines = (order.shipping_address or "").splitlines()
        # Checkout snapshots store contact details before the street address.
        if len(lines) >= 4 and re.fullmatch(r"[6-9][0-9]{9}", lines[1]) and "@" in lines[2]:
            order.checkout_name, order.checkout_phone, order.checkout_email = lines[:3]
            order.checkout_address = "\n".join(lines[3:])
        else:
            order.checkout_name = order.user.get_full_name() or order.user.username
            profile = getattr(order.user, "customer_profile", None)
            order.checkout_phone = profile.phone if profile else ""
            order.checkout_email = order.user.email
            order.checkout_address = order.shipping_address
        order.display_date = order.created_at.astimezone(zone).strftime("%d %b %Y, %I:%M %p IST")
    return render(request, "shop/admin/orders.html", {
        "admin_page": "orders",
        "products": Product.objects.select_related("category").all(),
        "categories": Category.objects.all(),
        "today_orders": daily.count(),
        "low_stock": Product.objects.filter(stock__lte=5).count(),
        "pending_orders": Order.objects.filter(status="pending").count(),
        "today_sales": daily.exclude(status="cancelled").aggregate(total=Sum("total_amount"))["total"] or Decimal("0"),
        "today_order_list": page, "orders_page": page, "show_all_orders": show_all,
        "order_status_choices": Order._meta.get_field("status").choices,
    })


# =========================
# ADD PRODUCT
# =========================

@admin_required
def add_product(request):

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Product added successfully."
            )

            return redirect("admin_dashboard")

    else:

        form = ProductForm()

    return render(
        request,
        "shop/admin/product_form.html",
        {
            "form": form,
            "title": "Add Product",
            "button_text": "Add Product",
        }
    )


# =========================
# EDIT PRODUCT
# =========================

@admin_required
def edit_product(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Product updated successfully."
            )

            return redirect("admin_dashboard")

    else:

        form = ProductForm(
            instance=product
        )

    return render(
        request,
        "shop/admin/product_form.html",
        {
            "form": form,
            "product": product,
            "title": "Edit Product",
            "button_text": "Update Product",
        }
    )


# =========================
# DELETE PRODUCT
# =========================

@admin_required
def delete_product(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == "POST":

        product.delete()

        messages.success(
            request,
            "Product deleted successfully."
        )

        return redirect("admin_dashboard")

    return render(
        request,
        "shop/admin/product_confirm_delete.html",
        {
            "product": product
        }
    )



def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related("category"), pk=product_id)
    saved = request.user.is_authenticated and Wishlist.objects.filter(
        user=request.user, product=product
    ).exists()
    record_view(request, product.pk)
    return render(request, "shop/product_detail.html", {
        "product": product, "is_saved": saved,
        "recommended_products": similar_to(request, product, limit=4),
        "wishlist_product_ids": wishlist_ids(request),
    })


@customer_required
def checkout_customer(request):
    import uuid
    from .forms import CheckoutCustomerForm
    from .checkout import place_order
    if not CartItem.objects.filter(cart__user=request.user).exists():
        return redirect("orders" if request.method == "POST" else "cart")
    if "checkout_token" not in request.session:
        request.session["checkout_token"] = "NK-" + uuid.uuid4().hex[:24]
    profile = CustomerProfile.objects.filter(user=request.user).first()
    initial = {
        "name": request.user.get_full_name(), "email": request.user.email,
        "mobile": profile.phone if profile else "",
        "address": profile.address if profile else "", "city": profile.city if profile else "",
        "state": profile.state if profile else "", "pincode": profile.pincode if profile else "",
    }
    initial.update(request.session.get("checkout_customer", {}))
    form = CheckoutCustomerForm(request.POST if request.method == "POST" else None, initial=initial)
    if request.method == "POST" and form.is_valid():
        token = request.POST.get("checkout_token", "")
        if token != request.session["checkout_token"]:
            form.add_error(None, "This checkout has expired. Please review and submit again.")
        else:
            try:
                order = place_order(request.user, form.cleaned_data, token)
            except ValueError as error:
                form.add_error(None, str(error))
            else:
                send_order_confirmation(order, form.cleaned_data)
                request.session["checkout_customer"] = form.cleaned_data
                request.session.pop("checkout_token", None)
                messages.success(request, "Your order has been placed. Awaiting store confirmation. Payment: Cash on Delivery.")
                return redirect("orders")
    return render(request, "shop/checkout_customer.html", {"form": form, "checkout_token": request.session["checkout_token"]})


@customer_required
def cancel_customer_order(request, order_id):
    from django.http import HttpResponseNotAllowed
    from .checkout import cancel_order
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    get_object_or_404(Order, pk=order_id, user=request.user)
    if cancel_order(request.user, order_id):
        messages.success(request, "Your order has been cancelled.")
    else:
        messages.info(request, "Only pending orders can be cancelled here. Contact the store for other orders.")
    return redirect("orders")

def send_order_confirmation(order, data):
    """Email the customer after an order is placed. Never blocks the order."""
    from django.core.mail import send_mail

    email = (data.get("email") or "").strip()
    if not email:
        return

    name = data.get("name") or "Customer"
    order_no = getattr(order, "pk", None)
    ref = f"#{order_no}" if order_no else ""

    address = (data.get("address") or "").strip()
    place = f"{data.get('city', '')}, {data.get('state', '')} - {data.get('pincode', '')}"
    ref_text = f", referenced as {ref}" if ref else ""

    body = (
        f"Dear {name},\n\n"
        f"Thank you for your recent purchase from NIKI Jewels. We are pleased to confirm "
        f"that we have successfully received your order{ref_text}.\n\n"
        f"Our team is now processing your request. Please note that at this stage, your "
        f"payment has not yet been processed. One of our dedicated account representatives "
        f"will contact you shortly to review your order details and guide you through the "
        f"secure payment and confirmation process.\n\n"
        f"Here is your specified shipping destination:\n\n"
        f"Delivery details:\n"
        f"{address}\n"
        f"{place}\n"
        f"Contact Mobile: {data.get('mobile', '')}\n\n"
        f"Sincerely,\n"
        f"The Team at NIKI Jewels\n"
        f"Timeless Beauty, Lasting Quality"
    )

    try:
        send_mail(
            subject=f"Order {ref} received - NIKI Jewels".replace("  ", " "),
            message=body,
            from_email=None,                 # uses DEFAULT_FROM_EMAIL
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as exc:
        print("Order email failed:", exc)    # order is still placed