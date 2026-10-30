"""Forgot-password (verified by phone number) and the admin Settings page.

* forgot_password  - customer enters username/e-mail + the phone number saved on their account
* reset_password   - if the phone matched, they choose a new password
* admin_settings   - admin sees who logged in and when, and can change the admin password

No SMS gateway is used: "verify" means the phone number must match the one the customer
saved in My Profile (or gave at checkout). To send a real OTP later, replace
_phone_matches() with a call to your SMS provider (MSG91, Twilio, ...).
"""
import re
import time
from datetime import timedelta
from zoneinfo import ZoneInfo

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Order
from .roles import admin_required, home_url_for, is_admin_role

IST = ZoneInfo("Asia/Kolkata")

MAX_TRIES = 5                 # wrong attempts allowed ...
LOCK_SECONDS = 15 * 60        # ... then locked for 15 minutes
RESET_WINDOW_SECONDS = 10 * 60  # time allowed to type the new password after verifying


# ------------------------------------------------------------------ helpers

def _digits(value):
    """'+91 78458-77124' -> '7845877124' (last 10 digits, or '' if fewer than 10)."""
    d = re.sub(r"\D", "", value or "")
    return d[-10:] if len(d) >= 10 else ""


def _client_ip(request):
    return request.META.get("REMOTE_ADDR", "")


def _find_account(identifier):
    """Username (any case) or a unique e-mail address."""
    account = User.objects.filter(username__iexact=identifier).first()
    if account is None and "@" in identifier:
        matches = User.objects.filter(email__iexact=identifier)
        account = matches.first() if matches.count() == 1 else None
    return account


def _phone_matches(account, phone):
    """True when `phone` equals a number we hold for this customer."""
    wanted = _digits(phone)
    if not wanted:
        return False

    known = set()
    profile = getattr(account, "customer_profile", None)
    if profile is not None:
        known.add(_digits(getattr(profile, "phone", "")))

    # Phone typed at checkout is stored on the 2nd line of the order's address snapshot.
    for address in Order.objects.filter(user=account).values_list("shipping_address", flat=True)[:20]:
        lines = (address or "").splitlines()
        if len(lines) >= 4:
            known.add(_digits(lines[1]))

    known.discard("")
    return wanted in known


def _ist(dt):
    return dt.astimezone(IST).strftime("%d %b %Y, %I:%M %p") if dt else ""


# ------------------------------------------------------------------ forgot password

def forgot_password(request):

    if request.user.is_authenticated:
        return redirect(home_url_for(request.user))

    identifier = ""

    if request.method == "POST":

        identifier = request.POST.get("identifier", "").strip()
        phone = request.POST.get("phone", "").strip()

        lock_key = f"pwreset:{identifier.lower()}:{_client_ip(request)}"
        tries = cache.get(lock_key, 0)

        if not identifier or not phone:
            messages.error(request, "Please enter your username (or e-mail) and phone number.")

        elif tries >= MAX_TRIES:
            messages.error(request, "Too many attempts. Please try again after 15 minutes.")

        else:
            account = _find_account(identifier)

            ok = (
                account is not None
                and account.is_active
                and not is_admin_role(account)        # admin passwords are never reset from the public page
                and not account.is_staff
                and not account.is_superuser
                and _phone_matches(account, phone)
            )

            if ok:
                cache.delete(lock_key)
                request.session["pw_reset_uid"] = account.pk
                request.session["pw_reset_until"] = time.time() + RESET_WINDOW_SECONDS
                return redirect("reset_password")

            cache.set(lock_key, tries + 1, LOCK_SECONDS)
            # Same message for every failure, so nobody can use this page to find out who has an account.
            messages.error(
                request,
                "We could not verify those details. Check the username and the phone number saved on your account."
            )

    return render(request, "shop/forgot_password.html", {"identifier": identifier})


# ------------------------------------------------------------------ choose a new password

def reset_password(request):

    uid = request.session.get("pw_reset_uid")
    until = request.session.get("pw_reset_until", 0)

    account = User.objects.filter(pk=uid, is_active=True).first() if uid else None

    if account is None or time.time() > until or is_admin_role(account) or account.is_staff or account.is_superuser:
        request.session.pop("pw_reset_uid", None)
        request.session.pop("pw_reset_until", None)
        messages.error(request, "Please verify your phone number again.")
        return redirect("forgot_password")

    error = ""

    if request.method == "POST":

        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if password1 != password2:
            error = "The two passwords do not match."
        else:
            try:
                validate_password(password1, user=account)
            except ValidationError as exc:
                error = " ".join(exc.messages)

        if not error:
            account.set_password(password1)
            account.save(update_fields=["password"])
            request.session.pop("pw_reset_uid", None)
            request.session.pop("pw_reset_until", None)
            messages.success(request, "Your password has been changed. Please log in.")
            return redirect("login")

    return render(request, "shop/reset_password.html", {"error": error, "reset_username": account.username})


# ------------------------------------------------------------------ admin settings

@admin_required
def admin_settings(request):

    password_error = ""

    if request.method == "POST" and request.POST.get("action") == "change_password":

        current = request.POST.get("current_password", "")
        new1 = request.POST.get("new_password1", "")
        new2 = request.POST.get("new_password2", "")

        if not request.user.check_password(current):
            password_error = "Your current password is not correct."
        elif new1 != new2:
            password_error = "The two new passwords do not match."
        elif new1 == current:
            password_error = "The new password must be different from the current one."
        else:
            try:
                validate_password(new1, user=request.user)
            except ValidationError as exc:
                password_error = " ".join(exc.messages)

        if not password_error:
            request.user.set_password(new1)
            request.user.save(update_fields=["password"])
            update_session_auth_hash(request, request.user)   # stay logged in
            messages.success(request, "Admin password changed.")
            return redirect("admin_settings")

    # ---- who has logged in ----
    q = request.GET.get("q", "").strip()
    show = request.GET.get("show", "all")

    users = User.objects.all()
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q))
    if show == "recent":
        users = users.filter(last_login__gte=timezone.now() - timedelta(days=7))
    elif show == "never":
        users = users.filter(last_login__isnull=True)
    users = users.order_by("-last_login", "-date_joined")

    page = Paginator(users, 20).get_page(request.GET.get("page"))
    for u in page:
        u.role_label = "Admin" if (is_admin_role(u) or u.is_staff or u.is_superuser) else "Customer"
        u.last_login_text = _ist(u.last_login)
        u.joined_text = _ist(u.date_joined)

    return render(request, "shop/admin/settings.html", {
        "admin_page": "settings",
        "password_error": password_error,
        "users_page": page,
        "q": q,
        "show": show,
        "total_users": User.objects.count(),
        "recent_users": User.objects.filter(last_login__gte=timezone.now() - timedelta(days=7)).count(),
        "never_users": User.objects.filter(last_login__isnull=True).count(),
    })
