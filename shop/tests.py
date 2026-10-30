from django.contrib.auth.models import User
from django.test import TestCase

from .models import Category, CustomerProfile, Product


GOOD_PASSWORD = "Gold#Shop2026"


def make_product():
    category = Category.objects.create(name="Rings")
    return Product.objects.create(
        category=category,
        name="Test Ring",
        description="A ring",
        price="1000.00",
        gender="girl",
        material="gold",
        stock=3,
    )


class RegisterTests(TestCase):
    """/register/ : username, email, create password, confirm password."""

    def register(self, **overrides):
        data = {
            "username": "newbuyer",
            "email": "new@example.com",
            "password1": GOOD_PASSWORD,
            "password2": GOOD_PASSWORD,
        }
        data.update(overrides)
        return self.client.post("/register/", data)

    def test_register_page_opens(self):
        self.assertEqual(self.client.get("/register/").status_code, 200)

    def test_register_creates_customer_and_logs_in(self):
        r = self.register()
        self.assertRedirects(r, "/account/", fetch_redirect_response=False)

        user = User.objects.get(username="newbuyer")
        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(user.check_password(GOOD_PASSWORD))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(CustomerProfile.objects.filter(user=user).exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_cannot_register_as_admin(self):
        self.register(is_staff="on", is_superuser="on")
        user = User.objects.get(username="newbuyer")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_passwords_must_match(self):
        r = self.register(password2="Different#Pass1")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username="newbuyer").exists())

    def test_weak_password_rejected(self):
        r = self.register(password1="12345", password2="12345")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username="newbuyer").exists())

    def test_username_and_email_must_be_unique(self):
        User.objects.create_user("taken", email="taken@example.com")

        self.register(username="Taken")
        self.assertFalse(User.objects.filter(username="newbuyer").exists())

        self.register(email="TAKEN@example.com")
        self.assertFalse(User.objects.filter(username="newbuyer").exists())

    def test_register_returns_to_requested_page(self):
        r = self.client.post("/register/", {
            "username": "newbuyer", "email": "new@example.com",
            "password1": GOOD_PASSWORD, "password2": GOOD_PASSWORD,
            "next": "/cart/",
        })
        self.assertRedirects(r, "/cart/", fetch_redirect_response=False)


class RoleBasedAccessTests(TestCase):
    """
    One site, one login page, two roles:
        admin    = is_staff / is_superuser  -> dashboard + product pages
        customer = any other logged-in user -> account, cart, wishlist, orders
    """

    def setUp(self):
        self.admin = User.objects.create_user(
            "owner", email="owner@example.com",
            password=GOOD_PASSWORD, is_staff=True,
        )
        self.customer = User.objects.create_user(
            "buyer", email="buyer@example.com", password=GOOD_PASSWORD,
        )
        CustomerProfile.objects.create(user=self.customer)

    # ---------------- login ----------------

    def test_login_page_opens(self):
        self.assertEqual(self.client.get("/login/").status_code, 200)

    def test_admin_login_lands_on_dashboard(self):
        r = self.client.post(
            "/login/", {"username": "owner", "password": GOOD_PASSWORD}
        )
        self.assertRedirects(
            r, "/admin-dashboard/", fetch_redirect_response=False
        )

    def test_customer_login_lands_on_account(self):
        r = self.client.post(
            "/login/", {"username": "buyer", "password": GOOD_PASSWORD}
        )
        self.assertRedirects(r, "/account/", fetch_redirect_response=False)

    def test_wrong_password_does_not_log_in(self):
        r = self.client.post(
            "/login/", {"username": "buyer", "password": "wrong"}
        )
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_returns_to_requested_page(self):
        r = self.client.post("/login/", {
            "username": "buyer", "password": GOOD_PASSWORD, "next": "/cart/",
        })
        self.assertRedirects(r, "/cart/", fetch_redirect_response=False)

    def test_login_ignores_unsafe_next(self):
        r = self.client.post("/login/", {
            "username": "buyer", "password": GOOD_PASSWORD,
            "next": "https://evil.example.com/",
        })
        self.assertRedirects(r, "/account/", fetch_redirect_response=False)

    def test_customer_never_sent_to_admin_page_by_next(self):
        r = self.client.post("/login/", {
            "username": "buyer", "password": GOOD_PASSWORD,
            "next": "/admin-dashboard/",
        })
        self.assertRedirects(r, "/account/", fetch_redirect_response=False)

    def test_logged_in_users_skip_login_and_register(self):
        self.client.force_login(self.customer)
        for path in ("/login/", "/register/"):
            self.assertRedirects(
                self.client.get(path), "/account/",
                fetch_redirect_response=False,
            )

        self.client.force_login(self.admin)
        for path in ("/login/", "/register/"):
            self.assertRedirects(
                self.client.get(path), "/admin-dashboard/",
                fetch_redirect_response=False,
            )

    # ---------------- anonymous ----------------

    def test_anonymous_is_sent_to_login_and_remembered(self):
        for path in ("/cart/", "/wishlist/", "/account/", "/orders/"):
            r = self.client.get(path)
            self.assertRedirects(
                r, f"/login/?next={path}", fetch_redirect_response=False
            )

    def test_anonymous_cannot_open_admin_pages(self):
        for path in (
            "/admin-dashboard/",
            "/admin-dashboard/product/add/",
        ):
            r = self.client.get(path)
            self.assertRedirects(
                r, f"/login/?next={path}", fetch_redirect_response=False
            )

    def test_public_pages_open_for_everyone(self):
        for path in ("/", "/collections/", "/about/", "/contact/"):
            self.assertEqual(self.client.get(path).status_code, 200, path)

    # ---------------- customer ----------------

    def test_customer_cannot_open_admin_pages(self):
        product = make_product()
        self.client.force_login(self.customer)
        for path in (
            "/admin-dashboard/",
            "/admin-dashboard/product/add/",
            f"/admin-dashboard/product/edit/{product.id}/",
            f"/admin-dashboard/product/delete/{product.id}/",
        ):
            self.assertRedirects(
                self.client.get(path), "/account/",
                fetch_redirect_response=False,
            )

    def test_customer_cannot_delete_a_product(self):
        product = make_product()
        self.client.force_login(self.customer)
        self.client.post(f"/admin-dashboard/product/delete/{product.id}/")
        self.assertTrue(Product.objects.filter(id=product.id).exists())

    def test_customer_can_open_customer_pages(self):
        self.client.force_login(self.customer)
        for path in ("/account/", "/cart/", "/wishlist/"):
            self.assertEqual(self.client.get(path).status_code, 200, path)

    # ---------------- admin ----------------

    def test_admin_dashboard_product_form_and_confirm_pages(self):
        product = make_product()
        self.client.force_login(self.admin)
        for path in (
            "/admin-dashboard/",
            "/admin-dashboard/product/add/",
            f"/admin-dashboard/product/edit/{product.id}/",
            f"/admin-dashboard/product/delete/{product.id}/",
        ):
            self.assertEqual(self.client.get(path).status_code, 200, path)

    def test_admin_delete_needs_confirmation_then_deletes(self):
        product = make_product()
        self.client.force_login(self.admin)

        # opening the page only asks "are you sure?"
        self.client.get(f"/admin-dashboard/product/delete/{product.id}/")
        self.assertTrue(Product.objects.filter(id=product.id).exists())

        # confirming (POST) deletes
        r = self.client.post(f"/admin-dashboard/product/delete/{product.id}/")
        self.assertRedirects(
            r, "/admin-dashboard/", fetch_redirect_response=False
        )
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_admin_is_kept_out_of_customer_pages(self):
        self.client.force_login(self.admin)
        for path in ("/cart/", "/wishlist/", "/orders/", "/account/"):
            self.assertRedirects(
                self.client.get(path), "/admin-dashboard/",
                fetch_redirect_response=False,
            )

    def test_navbar_changes_with_role(self):
        self.client.force_login(self.admin)
        page = self.client.get("/")
        self.assertContains(page, 'title="Admin Dashboard"')
        self.assertNotContains(page, 'title="Cart"')

        self.client.force_login(self.customer)
        page = self.client.get("/")
        self.assertContains(page, 'title="Cart"')
        self.assertNotContains(page, 'title="Admin Dashboard"')

    # ---------------- logout ----------------

    def test_logout_destinations(self):
        self.client.force_login(self.admin)
        self.assertRedirects(
            self.client.get("/admin-logout/"), "/login/",
            fetch_redirect_response=False,
        )

        self.client.force_login(self.customer)
        self.assertRedirects(
            self.client.get("/logout/"), "/",
            fetch_redirect_response=False,
        )
