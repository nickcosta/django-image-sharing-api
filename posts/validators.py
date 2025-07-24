from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
import re


def validate_caption_length(value):
    """Validate caption is not empty and within limit"""
    if not value or len(value.strip()) == 0:
        raise ValidationError("Caption cannot be empty.")

    if len(value) > 100:
        raise ValidationError("Caption cannot exceed 100 characters.")


def validate_image_url_format(url):
    """Comprehensive image URL validation"""
    if not url:
        raise ValidationError("Image URL is required.")

    url_validator = URLValidator()
    try:
        url_validator(url)
    except ValidationError:
        raise ValidationError("Please provide a valid URL.")

    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"]
    url_lower = url.lower()

    if any(url_lower.endswith(ext) for ext in image_extensions):
        return
    valid_patterns = [
        r".*cloudinary\.com.*",
        r".*amazonaws\.com.*",
        r".*googleapis\.com.*",
        r".*imgur\.com.*",
        r".*unsplash\.com.*",
        r".*pexels\.com.*",
        r".*pixabay\.com.*",
        r".*freepik\.com.*",
        r".*picsum\.photos.*",
        r".*placeholder\.com.*",
        r".*via\.placeholder\.com.*",
    ]

    if any(re.match(pattern, url_lower) for pattern in valid_patterns):
        return
    # Needs an image extension
    raise ValidationError(
        "Make sure you're linking directly to an image file (like .jpg, .png, etc.)"
    )
