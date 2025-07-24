from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class FollowQuerySet(models.QuerySet):
    """Custom QuerySet for Follow model"""

    def with_users(self):
        """Select related users to avoid N+1 queries"""
        return self.select_related("follower", "following")

    def followers_of(self, user):
        """Get all followers of a user"""
        return self.filter(following=user).select_related("follower")

    def following_of(self, user):
        """Get all user that a user Is following"""

        return self.filter(follower=user).select_related("following")


class FollowManager(models.Manager):
    """Custom manager for Follow model"""

    def get_queryset(self):
        return FollowQuerySet(self.model, using=self._db)

    def with_users(self):
        return self.get_queryset().with_users()

    def followers_of(self, user):
        return self.get_queryset().followers_of(user)

    def following_of(self, user):
        return self.get_queryset().following_of(user)

    def is_following(self, follower, following):
        """Check if follower is following the other user"""
        return self.filter(follower=follower, following=following).exists()

    def follow_user(self, follower, following):
        """Follow a user with proper validation"""
        if follower == following:
            raise ValidationError("Users can only follow other users")

        follow, created = self.get_or_create(follower=follower, following=following)
        return follow, created

    def unfollow_user(self, follower, following):
        """Unfollow a user"""
        try:
            follow = self.get(follower=follower, following=following)
            follow.delete()
            return True
        except self.model.DoesNotExist:
            return False


class Follow(models.Model):

    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers_set"
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following_set",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # Use custom manager
    objects = FollowManager()

    class Meta:
        # Prevent duplicate follows
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follow"
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="prevent_self_follow",
            ),
        ]
        indexes = [
            models.Index(fields=["follower"]),
            models.Index(fields=["following"]),
            models.Index(fields=["follower", "following"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def clean(self):
        super().clean()
        if self.follower == self.following:
            raise ValidationError("Can't follow yourself")

    def save(self, *args, **kwargs):
        self.full_clean()  # handles validation
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class LikeQuerySet(models.QuerySet):
    """Custom QuerySet for Like model"""

    def with_post_and_user(self):
        """Select related post and user to avoid N+1 queries"""
        return self.select_related("user", "post", "post__user")

    def for_post(self, post):
        """Get all likes for a specific post"""
        return self.filter(post=post)

    def by_user(self, user):
        """Get all likes by a specific user"""
        return self.filter(user=user)


class LikeManager(models.Manager):
    """Custom manager for Like model"""

    def get_queryset(self):
        return LikeQuerySet(self.model, using=self._db)

    def with_post_and_user(self):
        return self.get_queryset().with_post_and_user()

    def for_post(self, post):
        return self.get_queryset().for_post(post)

    def by_user(self, user):
        return self.get_queryset().by_user(user)

    def is_liked_by(self, user, post):
        """Check if user has liked a post"""
        return self.filter(user=user, post=post).exists()

    def like_post(self, user, post):
        """Like a post with proper validation"""
        like, created = self.get_or_create(user=user, post=post)
        return like, created

    def unlike_post(self, user, post):
        """Unlike a post"""
        try:
            like = self.get(user=user, post=post)
            like.delete()
            return True
        except self.model.DoesNotExist:
            return False


class Like(models.Model):
    """
    Model representing a user liking a post
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(
        "posts.Post", on_delete=models.CASCADE, related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Use custom manager
    objects = LikeManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_like")
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["post"]),
            models.Index(fields=["user", "post"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["post", "-created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"

    def clean(self):
        """Model-level validation"""
        super().clean()
        if self.user == self.post.user:
            raise ValidationError("Users cannot like their own posts.")
