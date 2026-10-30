"""
Role-based access for the whole site.

There is ONE website. Who you are decides what you can see:

    anonymous -> public pages only (home, collections, about, contact)
    customer  -> public pages + cart, wishlist, orders, profile, account
    admin     -> public pages + admin dashboard and product management

A user's role comes from Django's own flags, so no extra table is needed:
    is_staff or is_superuser  -> admin
    any other logged-in user  -> customer

To make someone an admin:  python manage.py createsuperuser
(or tick "Staff status" for the user in /admin/).

If you later want more roles (manager, delivery, ...), add them here and
use  @role_required("manager")  on the views - nothing else needs to change.
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


ROLE_ANONYMOUS = "anonymous"
ROLE_CUSTOMER = "customer"
ROLE_ADMIN = "admin"

# Where each role lands after login (URL names)
ROLE_HOME = {
    ROLE_ADMIN: "admin_dashboard",
    ROLE_CUSTOMER: "account",
    ROLE_ANONYMOUS: "home",
}

# Paths reserved for one role. Used so a stale ?next= value can never
# send a customer to an admin page, or an admin to a customer-only page.
ADMIN_PATH_PREFIXES = ("/admin-dashboard/", "/admin/")
CUSTOMER_PATH_PREFIXES = (
    "/cart/", "/wishlist/", "/orders/", "/account/", "/profile/",
)


# --------------------------------------------------------------------
# Role detection
# --------------------------------------------------------------------

def get_role(user):
    """Return ROLE_ADMIN, ROLE_CUSTOMER or ROLE_ANONYMOUS for a user."""

    if not user.is_authenticated:
        return ROLE_ANONYMOUS

    if user.is_staff or user.is_superuser:
        return ROLE_ADMIN

    return ROLE_CUSTOMER


def is_admin_role(user):
    return get_role(user) == ROLE_ADMIN


def home_url_for(user):
    """Landing page for the user's role."""
    return reverse(ROLE_HOME[get_role(user)])


# --------------------------------------------------------------------
# View protection
# --------------------------------------------------------------------

def role_required(*roles):
    """
    Allow a view only for the given roles.

    - Not logged in            -> sent to the login page (and brought back
                                  to this page afterwards)
    - Logged in, wrong role    -> sent to their own home with a message
    """

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            role = get_role(request.user)

            if role == ROLE_ANONYMOUS:
                return redirect_to_login(
                    request.get_full_path(),
                    reverse("login"),
                )

            if role not in roles:
                messages.error(
                    request,
                    "You do not have access to that page."
                )
                return redirect(home_url_for(request.user))

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


admin_required = role_required(ROLE_ADMIN)
customer_required = role_required(ROLE_CUSTOMER)


# --------------------------------------------------------------------
# "Take me back to where I was going" after login / register
# --------------------------------------------------------------------

def _is_safe_next(request, url):
    return bool(url) and url_has_allowed_host_and_scheme(
        url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    )


def get_next(request):
    """The ?next= page from the URL or the form, only if it is safe."""

    next_url = request.POST.get("next") or request.GET.get("next") or ""

    return next_url if _is_safe_next(request, next_url) else ""


def post_login_url(request, user):
    """
    Where to send a user right after they log in or register:
    the page they originally wanted (if it suits their role),
    otherwise the home page for their role.
    """

    next_url = get_next(request)

    if next_url:

        blocked = (
            CUSTOMER_PATH_PREFIXES if is_admin_role(user)
            else ADMIN_PATH_PREFIXES
        )

        if not next_url.startswith(blocked):
            return next_url

    return home_url_for(user)
