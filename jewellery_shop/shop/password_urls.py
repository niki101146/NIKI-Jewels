from django.urls import path

from . import password_views as v

urlpatterns = [
    path("forgot-password/", v.forgot_password, name="forgot_password"),
    path("reset-password/", v.reset_password, name="reset_password"),
    path("manage/settings/", v.admin_settings, name="admin_settings"),
]
