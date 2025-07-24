from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from django.db import transaction
from social.models import Follow, Like
from posts.models import Post
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Set up demo data for testing the feed system"

    def handle(self, *args, **options):
        with transaction.atomic():
            # Create demo users
            demo_users = [
                ("alice_photos", "Alice", "Photographer"),
                ("bob_foodie", "Bob", "Foodie"),
                ("carol_travel", "Carol", "Traveler"),
            ]

            created_users = []
            for username, first_name, last_name in demo_users:
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=f"{username}@demo.com",
                        password="demopass123",
                        first_name=first_name,
                        last_name=last_name,
                    )
                    from users.models import UserProfile

                    UserProfile.objects.create(user=user, bio=f"Demo user {first_name}")
                    created_users.append(user)
                    self.stdout.write(f"Created user: {username}")

            # Create follow relationships
            try:
                alice = User.objects.get(username="alice_photos")
                bob = User.objects.get(username="bob_foodie")
                carol = User.objects.get(username="carol_travel")

                Follow.objects.get_or_create(follower=bob, following=alice)
                Follow.objects.get_or_create(follower=carol, following=alice)
                Follow.objects.get_or_create(follower=carol, following=bob)
                self.stdout.write("Created follow relationships")
            except User.DoesNotExist:
                pass

            # Create demo posts
            demo_posts = [
                (
                    "alice_photos",
                    "Beautiful sunset",
                    "https://picsum.photos/500/500?random=1",
                ),
                (
                    "alice_photos",
                    "Street art discovery",
                    "https://picsum.photos/400/600?random=2",
                ),
                (
                    "bob_foodie",
                    "Delicious pasta",
                    "https://picsum.photos/600/400?random=3",
                ),
                ("bob_foodie", "Coffee art", "https://picsum.photos/400/400?random=4"),
                (
                    "carol_travel",
                    "Mountain view",
                    "https://picsum.photos/600/500?random=5",
                ),
                (
                    "carol_travel",
                    "City lights",
                    "https://picsum.photos/500/400?random=6",
                ),
            ]

            for username, caption, image_url in demo_posts:
                try:
                    user = User.objects.get(username=username)
                    Post.objects.create(user=user, caption=caption, image_url=image_url)
                    self.stdout.write(f"Created post: {caption} by {username}")
                except User.DoesNotExist:
                    continue

            # Create some likes
            try:
                bob = User.objects.get(username="bob_foodie")
                carol = User.objects.get(username="carol_travel")
                alice_posts = Post.objects.filter(user__username="alice_photos")

                for post in alice_posts:
                    Like.objects.get_or_create(user=bob, post=post)
                    Like.objects.get_or_create(user=carol, post=post)

                self.stdout.write("Created likes")
            except User.DoesNotExist:
                pass

            self.stdout.write(self.style.SUCCESS("Demo data created successfully!"))
            self.stdout.write("Demo accounts (password: demopass123):")
            self.stdout.write("  - alice_photos")
            self.stdout.write("  - bob_foodie")
            self.stdout.write("  - carol_travel")
