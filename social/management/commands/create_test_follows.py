from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from social.models import Follow
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Create test follow relationships for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of test follow relationships to create",
        )

    def handle(self, *args, **options):
        count = options["count"]

        # Get all users
        users = list(User.objects.all())
        if len(users) < 2:
            self.stdout.write(
                self.style.ERROR(
                    "Need at least 2 users to create follows. Create users first."
                )
            )
            return

        created_count = 0

        for i in range(count):
            # Pick two different random users
            follower = random.choice(users)
            following = random.choice([u for u in users if u != follower])

            try:
                # Try to create follow relationship
                follow, created = Follow.objects.follow_user(
                    follower=follower, following=following
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created follow: {follower.username} → {following.username}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Follow already exists: {follower.username} → {following.username}"
                        )
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create follow: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {created_count} new follow relationships!"
            )
        )

        # Show final stats
        total_follows = Follow.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f"Total follows in the database: {total_follows}")
        )
