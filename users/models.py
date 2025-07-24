from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Add related_name to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'auth_user'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]


class UserProfile(models.Model):
    """
    Extended user profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar_url = models.URLField(blank=True, null=True)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['followers_count']),
            models.Index(fields=['following_count']),
        ]

    def get_followers_count(self):
        """Get the number of followers"""
        return self.followers_set.count()
    
    def get_following_count(self):
        """Get the number of users this user is following"""
        return self.following_set.count()
    
    def is_following(self, user):
        """Check if this user is following another user"""
        from social.models import Follow
        return Follow.objects.is_following(self, user)
    
    def is_followed_by(self, user):
        """Check if this user is followed by another user"""
        from social.models import Follow
        return Follow.objects.is_following(user, self)
