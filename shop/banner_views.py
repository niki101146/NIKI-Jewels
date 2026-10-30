"""Admin screens for Hero Banners and Home Categories (admins only)."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .banner_forms import HeroBannerForm, HomeCategoryForm
from .banner_models import HeroBanner, HomeCategory
from .roles import admin_required

# The pictures that already sit in media/products/ - used by the "Load current ..." buttons so the
# owner can start from what the website shows today instead of from an empty list.
DEFAULT_BANNER = dict(
    image="products/hero image.png",
    eyebrow="TIMELESS ELEGANCE",
    heading="Jewellery That",
    highlight="Tells Your Story",
    subtitle="Discover beautiful jewellery designed for every special moment.",
    button_text="SHOP COLLECTION",
    order=1,
)

DEFAULT_CATEGORIES = [
    ("Rings", "ring", "products/ring.png"),
    ("Earrings", "earring", "products/earring.png"),
    ("Necklaces", "necklace", "products/necklace.png"),
    ("Bracelets", "bracelet", "products/bracelet.png"),
    ("Nose Ring", "nose ring", "products/nosering.png"),
    ("Anklet", "anklet", "products/anklet.png"),
    ("Bangles", "bangle", "products/bangles.png"),
    ("Chains", "chain", "products/chain1.png"),
    ("Pendants", "pendant", "products/pendant.png"),
    ("Toe Ring", "toe ring", "products/toe_ring.avif"),
    ("Mangalsutra", "mangalsutra", "products/mangalsutra.png"),
    ("Nose Pin", "nose pin", "products/nosepin.png"),
]


def _toggle(request, model, label):
    obj = get_object_or_404(model, pk=request.POST.get("id"))
    obj.is_active = not obj.is_active
    obj.save(update_fields=["is_active"])
    messages.success(request, f"{label} is now {'showing' if obj.is_active else 'hidden'}.")


def _save_form(request, form_class, instance, template, context, done_url, done_message):
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, done_message)
            return redirect(done_url)
    else:
        form = form_class(instance=instance)
    return render(request, template, dict(context, form=form, instance=instance))


# ----------------------------------------------------------------------------- hero banners
@admin_required
def admin_banners(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "toggle":
            _toggle(request, HeroBanner, "Banner")
        elif action == "load_defaults" and not HeroBanner.objects.exists():
            HeroBanner.objects.create(**DEFAULT_BANNER)
            messages.success(request, "Your current home banner was added. You can edit it now.")
        return redirect("admin_banners")
    return render(request, "shop/admin/banners.html", {
        "admin_page": "banners",
        "banners": HeroBanner.objects.all(),
    })


@admin_required
def add_banner(request):
    return _save_form(
        request, HeroBannerForm, None, "shop/admin/content_form.html",
        {"admin_page": "banners", "title": "Add Hero Banner", "button_text": "Save banner",
         "cancel_url": "admin_banners", "kind": "banner"},
        "admin_banners", "Banner added.",
    )


@admin_required
def edit_banner(request, banner_id):
    banner = get_object_or_404(HeroBanner, pk=banner_id)
    return _save_form(
        request, HeroBannerForm, banner, "shop/admin/content_form.html",
        {"admin_page": "banners", "title": "Edit Hero Banner", "button_text": "Update banner",
         "cancel_url": "admin_banners", "kind": "banner"},
        "admin_banners", "Banner updated.",
    )


@admin_required
def delete_banner(request, banner_id):
    banner = get_object_or_404(HeroBanner, pk=banner_id)
    if request.method == "POST":
        banner.delete()
        messages.success(request, "Banner deleted.")
        return redirect("admin_banners")
    return render(request, "shop/admin/content_confirm_delete.html", {
        "admin_page": "banners", "label": "banner", "name": str(banner),
        "image": banner.image, "cancel_url": "admin_banners",
    })


# ----------------------------------------------------------------------------- home categories
@admin_required
def admin_home_categories(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "toggle":
            _toggle(request, HomeCategory, "Category")
        elif action == "load_defaults" and not HomeCategory.objects.exists():
            HomeCategory.objects.bulk_create([
                HomeCategory(name=name, search_term=term, image=image, order=i)
                for i, (name, term, image) in enumerate(DEFAULT_CATEGORIES, start=1)
            ])
            messages.success(request, "Your current home categories were added. You can edit them now.")
        return redirect("admin_home_categories")
    return render(request, "shop/admin/home_categories.html", {
        "admin_page": "categories",
        "categories": HomeCategory.objects.all(),
    })


@admin_required
def add_home_category(request):
    return _save_form(
        request, HomeCategoryForm, None, "shop/admin/content_form.html",
        {"admin_page": "categories", "title": "Add Category", "button_text": "Save category",
         "cancel_url": "admin_home_categories", "kind": "category"},
        "admin_home_categories", "Category added.",
    )


@admin_required
def edit_home_category(request, category_id):
    category = get_object_or_404(HomeCategory, pk=category_id)
    return _save_form(
        request, HomeCategoryForm, category, "shop/admin/content_form.html",
        {"admin_page": "categories", "title": "Edit Category", "button_text": "Update category",
         "cancel_url": "admin_home_categories", "kind": "category"},
        "admin_home_categories", "Category updated.",
    )


@admin_required
def delete_home_category(request, category_id):
    category = get_object_or_404(HomeCategory, pk=category_id)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect("admin_home_categories")
    return render(request, "shop/admin/content_confirm_delete.html", {
        "admin_page": "categories", "label": "category", "name": category.name,
        "image": category.image, "cancel_url": "admin_home_categories",
    })
