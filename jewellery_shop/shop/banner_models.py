"""Content the shop owner manages from the admin area:

    HeroBanner    - the big picture + headline at the top of the home page (can be several = slider)
    HomeCategory  - the round / card category pictures in "Our Collections" on the home page

Import these in shop/models.py with one line (see SETUP_BANNERS.md) so Django creates the tables.
"""
from django.db import models


class HeroBanner(models.Model):
    image = models.ImageField(
        upload_to="banners/",
        help_text="Wide picture, best about 1920 x 800 px. Keep the left side darker/empty - the text sits there.",
    )
    eyebrow = models.CharField(
        "Small line above the heading", max_length=60, blank=True, default="TIMELESS ELEGANCE",
    )
    heading = models.CharField("Heading (white)", max_length=80, default="Jewellery That")
    highlight = models.CharField(
        "Heading second line (gold)", max_length=80, blank=True, default="Tells Your Story",
    )
    subtitle = models.CharField(max_length=200, blank=True)
    button_text = models.CharField(
        max_length=40, blank=True, default="SHOP COLLECTION",
        help_text="Leave empty to show no button.",
    )
    button_link = models.CharField(
        max_length=200, blank=True,
        help_text="Where the button goes. Leave empty to open the Collections page.",
    )
    is_active = models.BooleanField("Show on website", default=True)
    order = models.PositiveIntegerField(default=0, help_text="Smaller number shows first.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.heading} {self.highlight}".strip()


class HomeCategory(models.Model):
    name = models.CharField(max_length=60, help_text="Shown under the picture, e.g. Rings.")
    image = models.ImageField(
        upload_to="categories/",
        help_text="Square-ish picture (about 600 x 800 px).",
    )
    search_term = models.CharField(
        max_length=60, blank=True,
        help_text="What the Collections page searches for when tapped, e.g. ring. Leave empty to use the name.",
    )
    is_active = models.BooleanField("Show on website", default=True)
    order = models.PositiveIntegerField(default=0, help_text="Smaller number shows first.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "home categories"

    def __str__(self):
        return self.name

    @property
    def query(self):
        return (self.search_term or self.name).strip()
