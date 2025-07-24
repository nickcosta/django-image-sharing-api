from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from social.models import Like
from posts.models import Post
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Create test like relationships for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Number of test like relationships to create",
        )

    def handle(self, *args, **options):
        count = options["count"]

        # Get all users and posts
        users = list(User.objects.all())
        posts = list(Post.objects.all())

        if len(users) < 1:
            self.stdout.write(
                self.style.ERROR("Must have at least 1 user in order to create likes")
            )
            return
        num_of_posts = len(posts)
        if num_of_posts < 1:
            self.stdout.write(
                self.style.ERROR("Must have at least 1 user in order to create posts.")
            )
            return

        created_count = 0

        for i in range(count):
            # Pick random user and post
            user = random.choice(users)
            post = random.choice(posts)

            if user == post.user:
                continue

            try:
                # Try to create like relationship
                like, created = Like.objects.like_post(user=user, post=post)

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created like: {user.username} Post {post.id} ("{post.caption[:30]}...")'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Liked already: {user.username} Post {post.id}"
                        )
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create like: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {created_count} new like relationships!"
            )
        )

        # Show final stats
        total_likes = Like.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f"Total No of likes in the DB: {total_likes}")
        )

        # Show most liked posts using the existing like_count property
        self.stdout.write(self.style.SUCCESS("\n=== MOST LIKED POSTS ==="))
        for post in Post.objects.all()[:5]:
            like_count = post.like_count  # Use the property instead of annotation
            if like_count > 0:
                self.stdout.write(
                    f'Post {post.id}: "{post.caption}" by {post.user.username} - {like_count} likes'
                )
