from django import forms
from django.core.files.uploadedfile import UploadedFile

from .banner_models import HeroBanner, HomeCategory

MAX_IMAGE_MB = 8


class _ImageSizeMixin:
    def clean_image(self):
        image = self.cleaned_data.get("image")
        # only a brand-new upload is size-checked (an existing file is left alone)
        if isinstance(image, UploadedFile) and image.size > MAX_IMAGE_MB * 1024 * 1024:
            raise forms.ValidationError(
                f"This picture is too large. Please upload one under {MAX_IMAGE_MB} MB."
            )
        return image


class HeroBannerForm(_ImageSizeMixin, forms.ModelForm):
    class Meta:
        model = HeroBanner
        fields = [
            "image", "eyebrow", "heading", "highlight", "subtitle",
            "button_text", "button_link", "order", "is_active",
        ]
        widgets = {"image": forms.FileInput(attrs={"accept": "image/*"})}


class HomeCategoryForm(_ImageSizeMixin, forms.ModelForm):
    class Meta:
        model = HomeCategory
        fields = ["name", "image", "search_term", "order", "is_active"]
        widgets = {"image": forms.FileInput(attrs={"accept": "image/*"})}
