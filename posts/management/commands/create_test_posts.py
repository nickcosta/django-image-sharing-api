from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from posts.models import Post

import random

User = get_user_model()


class Command(BaseCommand):
    help = "Create test posts"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=10, help="Number of test posts to create"
        )

    def handle(self, *args, **options):
        count = options["count"]

        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.ERROR("No users found. Create users first."))
            return

        sample_images = [
            "https://picsum.photos/400/400?random=1",
            "https://picsum.photos/400/600?random=2",
            "https://picsum.photos/600/400?random=3",
            "https://picsum.photos/500/500?random=4",
            "https://picsum.photos/400/400?random=5",
            "https://picsum.photos/450/600?random=6",
            "https://picsum.photos/600/450?random=7",
            "https://picsum.photos/400/500?random=8",
            "https://picsum.photos/500/400?random=9",
            "https://picsum.photos/400/400?random=10",
        ]

        sample_captions = [
            "Beautiful sunny day",
            "Coffee, coding and good vibes",
            "Weekend fun",
            "Nature is beautiful",
            "Good everybody",
            "Feeling enthusiastic today",
            "Adventure beckons",
            "Delicious takeout",
            "WIP",
            "Perfect Day",
            "Netflix n Chill",
            "New amazing discovery",
            "Stay Hard",
            "I feel inspired",
            "Simply beautiful",
        ]

        created_count = 0

        for i in range(count):
            user = random.choice(users)

            image_url = random.choice(sample_images)
            caption = random.choice(sample_captions)

            try:
                post = Post.objects.create(
                    user=user, caption=caption, image_url=image_url
                )
                created_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created post {created_count}: "{caption}" by {user.username}'
                    )
                )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create post: {e}"))

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} test posts!")
        )
