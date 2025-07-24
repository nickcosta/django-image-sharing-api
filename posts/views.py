from rest_framework import generics, permissions, status
from .models import Post
from rest_framework.response import Response

from social.models import Follow
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from users.permissions import IsOwnerOrReadOnly
from .serializers import PostDetailSerializer, PostCreateSerializer, PostListSerializer


class PostListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Optimized queryset with user data and like counts"""
        return Post.objects.with_user().with_like_counts().ordered_by_recent()

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.request.method == "POST":
            return PostCreateSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        """Save post with current user"""
        serializer.save(user=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a post
    """

    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = PostDetailSerializer

    def get_queryset(self):
        return Post.objects.with_user().with_like_counts()

    def get_object(self):
        post_id = self.kwargs.get("pk")
        return get_object_or_404(self.get_queryset(), pk=post_id)


class PopularPostsView(generics.ListAPIView):

    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get posts ordered by like count"""
        from django.db.models import Count

        return (
            Post.objects.with_user()
            .annotate(total_likes=Count("likes"))
            .order_by("-total_likes", "-created_at")
        )


class UserPostsView(generics.ListAPIView):
    """
    List posts by a specific user
    """

    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get posts by specific user"""
        user_id = self.kwargs.get("user_id")
        return (
            Post.objects.with_user()
            .with_like_counts()
            .filter(user_id=user_id)
            .ordered_by_recent()
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_posts(request):
    """
    Get current user's posts
    """
    posts = (
        Post.objects.with_user()
        .with_like_counts()
        .filter(user=request.user)
        .ordered_by_recent()
    )

    serializer = PostListSerializer(posts, many=True, context={"request": request})

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def post_stats(request):
    """
    Get statistics about posts
    """
    total_posts = Post.objects.count()
    user_posts = Post.objects.filter(user=request.user).count()

    # Most liked post
    most_liked = Post.objects.with_like_counts().order_by("-total_likes").first()

    stats = {
        "total_posts": total_posts,
        "user_posts": user_posts,
        "most_liked_post": None,
    }

    if most_liked:
        stats["most_liked_post"] = {
            "id": most_liked.id,
            "caption": most_liked.caption,
            "total_likes": getattr(most_liked, "total_likes", 0),
            "user": most_liked.user.username,
        }

    return Response(stats)


class FeedView(generics.ListAPIView):

    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.feed_for_user(self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            following_count = Follow.objects.filter(follower=request.user).count()

            response_data = self.get_paginated_response(serializer.data).data
            response_data["feed_meta"] = {
                "following_count": following_count,
                "has_posts": len(serializer.data) > 0,
                "feed_type": "following_only",
            }
            return Response(response_data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TimelineView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.timeline_for_user(self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            from social.models import Follow

            following_count = Follow.objects.filter(follower=request.user).count()
            own_posts_count = Post.objects.filter(user=request.user).count()

            response_data = self.get_paginated_response(serializer.data).data
            response_data["timeline_meta"] = {
                "following_count": following_count,
                "own_posts_count": own_posts_count,
                "has_posts": len(serializer.data) > 0,
                "feed_type": "timeline",
            }
            return Response(response_data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DiscoverView(generics.ListAPIView):

    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from social.models import Follow

        # get users that current user follows plus self
        following_ids = list(
            Follow.objects.filter(follower=self.request.user).values_list(
                "following_id", flat=True
            )
        )
        following_ids.append(self.request.user.id)

        return (
            Post.objects.with_user()
            .exclude(user_id__in=following_ids)
            .ordered_by_recent()
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            response_data = self.get_paginated_response(serializer.data).data
            response_data["discover_meta"] = {
                "feed_type": "discover",
                "description": "Posts from users you don't follow",
            }
            return Response(response_data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def feed_stats(request):
    from social.models import Follow

    following_count = Follow.objects.filter(follower=request.user).count()
    followers_count = Follow.objects.filter(following=request.user).count()

    feed_posts_count = Post.objects.feed_for_user(request.user).count()
    timeline_posts_count = Post.objects.timeline_for_user(request.user).count()
    own_posts_count = Post.objects.filter(user=request.user).count()

    discover_posts_count = Post.objects.count() - timeline_posts_count

    stats = {
        "social_stats": {
            "following_count": following_count,
            "followers_count": followers_count,
        },
        "feed_stats": {
            "feed_posts": feed_posts_count,
            "timeline_posts": timeline_posts_count,
            "own_posts": own_posts_count,
            "discover_posts": discover_posts_count,
        },
        "recommendations": {
            "follow_more_users": following_count < 5,
            "create_posts": own_posts_count < 3,
            "explore_discover": discover_posts_count > 0,
        },
    }

    return Response(stats)
