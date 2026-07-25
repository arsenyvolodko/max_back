import os

from django import template

register = template.Library()

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}


def _ext(value):
    name = getattr(value, 'name', '') or str(value or '')
    return os.path.splitext(name)[1].lower()


@register.filter
def is_image(value):
    """True, если файл — картинка (по расширению)."""
    return bool(value) and _ext(value) in IMAGE_EXTS


@register.filter
def is_pdf(value):
    """True, если файл — PDF."""
    return bool(value) and _ext(value) == '.pdf'
