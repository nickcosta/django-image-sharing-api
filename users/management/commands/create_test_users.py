from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from users.models import UserProfile
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Create test users for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=5, help="Number of test users to create"
        )

    def handle(self, *args, **options):
        count = options["count"]

        # Create test users
        for i in range(1, count + 1):
            username = f"testuser{i}"
            email = f"test{i}@example.com"

            # Skip if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f"User {username} exists SO skipping")
                )
                continue

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password="testpass123",
                first_name=f"Test",
                last_name=f"User{i}",
            )

            # Create profile
            UserProfile.objects.create(
                user=user,
                bio=f"This is test user {i}",
                followers_count=random.randint(0, 100),
                following_count=random.randint(0, 50),
                posts_count=random.randint(0, 20),
            )

            # Create token
            Token.objects.create(user=user)

            self.stdout.write(
                self.style.SUCCESS(f"Successfully created user: {username}")
            )

        self.stdout.write(
            self.style.SUCCESS(f"Created {count} test users successfully!")
        )
        self.stdout.write(self.style.WARNING("All users have password: testpass123"))
