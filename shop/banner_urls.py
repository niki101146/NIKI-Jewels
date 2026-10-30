from django.urls import path

from . import banner_views as v

urlpatterns = [
    path("manage/banners/", v.admin_banners, name="admin_banners"),
    path("manage/banners/add/", v.add_banner, name="add_banner"),
    path("manage/banners/<int:banner_id>/edit/", v.edit_banner, name="edit_banner"),
    path("manage/banners/<int:banner_id>/delete/", v.delete_banner, name="delete_banner"),

    path("manage/categories/", v.admin_home_categories, name="admin_home_categories"),
    path("manage/categories/add/", v.add_home_category, name="add_home_category"),
    path("manage/categories/<int:category_id>/edit/", v.edit_home_category, name="edit_home_category"),
    path("manage/categories/<int:category_id>/delete/", v.delete_home_category, name="delete_home_category"),
]
