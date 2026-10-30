# Hero Banner + Home Category admin - 3 steps to switch it on

New files (already in the zip): `shop/banner_models.py`, `banner_forms.py`, `banner_views.py`,
`banner_urls.py`, 5 templates in `templates/shop/admin/`, `static/css/admin-content.css`,
`static/js/hero-slider.js`. The home view (`views.py`), `home.html` and the admin sidebar
(`admin/base.html`) were already edited for you.

Your zip did not include `models.py` and `urls.py`, so add these two small things yourself:

1. `shop/models.py` - add this line at the bottom:

       from .banner_models import HeroBanner, HomeCategory  # noqa: F401

2. `shop/urls.py` - add at the top, and at the bottom of the file:

       from .banner_urls import urlpatterns as banner_urlpatterns
       ...
       urlpatterns += banner_urlpatterns

   (If your project `urls.py` includes the shop urls with a prefix, the admin pages will be under it.)

3. Create the tables:

       python manage.py makemigrations shop
       python manage.py migrate

Then open the admin sidebar -> **Hero Banners** / **Categories**.
First time, click **Load current banner** / **Load current categories** so the list starts with what
the website shows today, then edit, add, hide or delete.

Until step 3 is done the home page keeps working with its built-in banner and categories.
