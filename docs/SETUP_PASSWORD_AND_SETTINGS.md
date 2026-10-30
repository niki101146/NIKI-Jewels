# Forgot password + Admin Settings - 1 step to switch on

New files: `shop/password_views.py`, `shop/password_urls.py`, `templates/shop/forgot_password.html`,
`reset_password.html`, `_auth_styles.html`, `templates/shop/admin/settings.html`.
Edited: `login.html` (Forgot password? link), `admin/base.html` (Settings link), `header-theme.css` (mobile header).

`shop/urls.py` - same way as the banners:

    from .password_urls import urlpatterns as password_urlpatterns
    ...
    urlpatterns += password_urlpatterns

No new database tables / migrations are needed.
