"""Automatically convert every uploaded image to WebP.

How it works: just before a model is saved, any NEW image that was uploaded
(Product, Category, Hero Banner, Home Category ...) is converted to .webp.
Images that are already .webp, and animated GIFs, are left alone.
If anything goes wrong the original image is saved as it was, so an upload never fails.

Turn it on with one line at the top of shop/models.py (see below). No migration needed.
"""
import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.db.models import ImageField
from django.db.models.signals import pre_save
from PIL import Image, ImageOps

WEBP_QUALITY = 85      # 1-100, higher = better picture, bigger file
MAX_SIDE = 2000        # longest side in px; larger pictures are scaled down


def convert_to_webp(field_file):
    """Convert one uploaded FieldFile to WebP (in place, before it is stored)."""
    if not field_file or getattr(field_file, "_committed", True):
        return  # nothing new was uploaded

    base, ext = os.path.splitext(os.path.basename(field_file.name))
    if ext.lower() == ".webp":
        return

    try:
        field_file.file.seek(0)
        img = Image.open(field_file.file)

        if getattr(img, "is_animated", False):
            field_file.file.seek(0)
            return  # keep animated GIFs as they are

        img = ImageOps.exif_transpose(img)  # fix phone photos that come out rotated
        has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
        img = img.convert("RGBA" if has_alpha else "RGB")

        if max(img.size) > MAX_SIDE:
            img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, "WEBP", quality=WEBP_QUALITY, method=6)
    except Exception:
        try:
            field_file.file.seek(0)
        except Exception:
            pass
        return  # not a readable image / WebP unsupported -> keep the original

    field_file.save(f"{base}.webp", ContentFile(buffer.getvalue()), save=False)


def _convert_images_before_save(sender, instance, **kwargs):
    for field in sender._meta.concrete_fields:
        if isinstance(field, ImageField):
            convert_to_webp(getattr(instance, field.name))


pre_save.connect(
    _convert_images_before_save,
    dispatch_uid="shop_convert_images_to_webp",
)