from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import re

User = get_user_model()


def validate_image_url(url):
    """Validate that URL appears to be an image URL"""
    if not url:
        return

    # Basic URL validation first
    url_validator = URLValidator()
    try:
        url_validator(url)
    except ValidationError:
        raise ValidationError("Invalid URL format.")

    # common image extensions
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
    url_lower = url.lower()

    if not any(url_lower.endswith(ext) for ext in image_extensions):
        # common CDN patterns
        cdn_patterns = [
            r".*cloudinary\.com.*",
            r".*amazonaws\.com.*",
            r".*googleapis\.com.*",
            r".*imgur\.com.*",
            r".*unsplash\.com.*",
            r".*picsum\.photos.*",
            r".*placeholder\.com.*",
        ]

        if not any(re.match(pattern, url_lower) for pattern in cdn_patterns):
            raise ValidationError(
                "Make sure the URL ends in a standard image file extension such as"
                ".jpg, .jpeg, .png, .gif, .webp, or .bmp."
            )


class PostQuerySet(models.QuerySet):
    """Custom QuerySet for Post model"""

    def with_user(self):
        """Select related user to avoid N+1 queries"""
        return self.select_related("user", "user__profile")

    def with_like_counts(self):
        """Annotate with like counts"""
        return self.annotate(total_likes=models.Count("likes", distinct=True))

    def ordered_by_recent(self):
        """Order by most recent first"""
        return self.order_by("-created_at")

    def ordered_by_likes(self):
        """Order by most liked first, then by recent"""
        return self.with_like_counts().order_by("-total_likes", "-created_at")


class PostManager(models.Manager):
    """Custom manager for Post model"""

    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def with_user(self):
        return self.get_queryset().with_user()

    def with_like_counts(self):
        return self.get_queryset().with_like_counts()

    def recent(self):
        return self.get_queryset().with_user().ordered_by_recent()

    def popular(self):
        return self.get_queryset().with_user().ordered_by_likes()

    def feed_for_user(self, user):
        """Get feed posts for a user (posts from users they follow)"""
        from social.models import Follow

        # Get IDs of users that the current user follows
        following_ids = Follow.objects.filter(follower=user).values_list(
            "following_id", flat=True
        )

        # Return posts from followed users, optimized but without annotation conflict
        return (
            self.get_queryset()
            .with_user()
            .filter(user_id__in=following_ids)
            .ordered_by_recent()
        )

    def timeline_for_user(self, user):
        """Get the timeline for a user (their posts & posts from people they follow)"""
        from social.models import Follow

        # Get the IDs of people the user follows, plus the user's own ID.
        following_ids = list(
            Follow.objects.filter(follower=user).values_list("following_id", flat=True)
        )
        following_ids.append(user.id)  # Remember the user's own posts!

        # Get posts from followed users and the user, sorted by most recent.
        return (
            self.get_queryset()
            .with_user()
            .filter(user_id__in=following_ids)
            .ordered_by_recent()
        )


class Post(models.Model):
    """
    Post model representing an image post in the social media app
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    caption = models.CharField(
        max_length=100, help_text="Caption for the image (max 100 characters)"
    )
    image_url = models.URLField(
        validators=[validate_image_url], help_text="URL to the image stored in CDN"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use custom manager
    objects = PostManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["-created_at"]),  # For reverse ordering
            models.Index(fields=["user", "-created_at"]),  # Composite index
        ]

    def __str__(self):
        return f"{self.user.username}: {self.caption[:30]}..."

    def clean(self):
        """Model-level validation"""
        super().clean()

        # Validate caption length
        if len(self.caption.strip()) == 0:
            raise ValidationError({"caption": "Caption cannot be empty."})

        # Additional image URL validation
        if self.image_url:
            validate_image_url(self.image_url)

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def like_count(self):
        """Get like count for this post"""
        return self.likes.count()

    def is_liked_by(self, user):
        """Check if post is liked by given user"""
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()

    def feed_for_user(self, user):
        """Get feed posts for a user (posts from users they follow)"""
        from social.models import Follow

        # Get IDs of users that the current user follows
        following_ids = Follow.objects.filter(follower=user).values_list(
            "following_id", flat=True
        )

        # Return posts from followed users, optimized but without annotation conflict
        return (
            self.get_queryset()
            .with_user()
            .filter(user_id__in=following_ids)
            .ordered_by_recent()
        )

    def timeline_for_user(self, user):
        """Users posts and those they follow"""
        from social.models import Follow

        following_ids = list(
            Follow.objects.filter(follower=user).values_list(following_id, flat=True)
        )
        # Include user's own posts
        following_ids.append(user.id)

        # Return posts from followed users + own posts
        return (
            self.get_queryset()
            .with_user()
            .filter(user_id__in=following_ids)
            .ordered_by_recent()
        )
