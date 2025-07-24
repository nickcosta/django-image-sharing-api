from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef
from rest_framework.response import Response
from posts.models import Post
from django.db import transaction
from .models import Follow
from .serializers import (
    FollowSerializer,
    FollowCreateSerializer,
    FollowerListSerializer,
    FollowingListSerializer,
    FollowStatsSerializer,
)

User = get_user_model()


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, user_id):
    """
    Follow a user
    """
    user_to_follow = get_object_or_404(User, pk=user_id)

    # Check if trying to follow self
    if request.user == user_to_follow:
        return Response(
            {"error": "You cannot follow yourself."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if Follow.objects.is_following(request.user, user_to_follow):
        return Response({"message": "Already following"})

    # Create follow relationship

    follow, created = Follow.objects.follow_user(
        follower=request.user, following=user_to_follow
    )

    # Update follower counts (we'll optimize this later with signals)

    serializer = FollowSerializer(follow, context={"request": request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request, user_id):
    """
    Unfollow a user
    """
    try:
        user_to_unfollow = get_object_or_404(User, pk=user_id)

        # Check if actually following
        if not Follow.objects.is_following(request.user, user_to_unfollow):
            return Response(
                {"error": "You are not following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Remove follow relationship
        with transaction.atomic():
            success = Follow.objects.unfollow_user(
                follower=request.user, following=user_to_unfollow
            )

            if success:
                return Response(
                    {"message": f"You have unfollowed {user_to_unfollow.username}."}
                )
            else:
                return Response(
                    {"error": "Unable to unfollow user."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserFollowersView(generics.ListAPIView):
    serializer_class = FollowerListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        user = get_object_or_404(User, pk=user_id)
        return Follow.objects.followers_of(user)


class UserFollowingView(generics.ListAPIView):
    serializer_class = FollowingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get users that the specified user is following"""
        user_id = self.kwargs.get("user_id")
        user = get_object_or_404(User, pk=user_id)
        return Follow.objects.following_of(user)


class MyFollowersView(generics.ListAPIView):
    """
    List current user's followers
    """

    serializer_class = FollowerListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.followers_of(self.request.user)


class MyFollowingView(generics.ListAPIView):

    serializer_class = FollowingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get users that current user is following"""
        return Follow.objects.following_of(self.request.user)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def follow_stats(request, user_id=None):
    """
    Get follow statistics for a user
    """
    if user_id:
        target_user = get_object_or_404(User, pk=user_id)
    else:
        target_user = request.user

    # Get counts using efficient queries
    followers_count = Follow.objects.filter(following=target_user).count()
    following_count = Follow.objects.filter(follower=target_user).count()
    is_following = False
    is_followed_by = False
    mutual_follows = 0

    if target_user != request.user:
        is_following = Follow.objects.is_following(request.user, target_user)
        is_followed_by = Follow.objects.is_following(target_user, request.user)

        current_user_following = Follow.objects.filter(
            follower=request.user
        ).values_list("following", flat=True)

        target_user_following = Follow.objects.filter(follower=target_user).values_list(
            "following", flat=True
        )

        mutual_follows = len(set(current_user_following) & set(target_user_following))

    stats = {
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "is_followed_by": is_followed_by,
        "mutual_follows": mutual_follows,
    }

    serializer = FollowStatsSerializer(stats)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def suggested_users(request):
    following_ids = Follow.objects.filter(follower=request.user).values_list(
        "following_id", flat=True
    )

    suggested = (
        User.objects.exclude(id__in=list(following_ids) + [request.user.id])
        .annotate(followers_count=Count("followers_set"))
        .order_by("-followers_count")[:10]
    )

    from users.serializers import UserListSerializer

    serializer = UserListSerializer(suggested, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def mutual_follows(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    if target_user == request.user:
        return Response(
            {"error": "Cannot get mutual follows with yourself."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    current_user_following = Follow.objects.filter(follower=request.user).values_list(
        "following", flat=True
    )

    target_user_following = Follow.objects.filter(follower=target_user).values_list(
        "following", flat=True
    )

    mutual_user_ids = set(current_user_following) & set(target_user_following)
    mutual_users = User.objects.filter(id__in=mutual_user_ids)

    from users.serializers import UserListSerializer

    serializer = UserListSerializer(
        mutual_users, many=True, context={"request": request}
    )

    return Response({"count": len(mutual_user_ids), "users": serializer.data})


from .models import Like
from .serializers import (
    LikeSerializer,
    LikeCreateSerializer,
    PostLikeSerializer,
    UserLikeSerializer,
    LikeStatsSerializer,
)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def like_post(request, post_id):
    """
    Like a post
    """
    from posts.models import Post

    try:
        post = get_object_or_404(Post, pk=post_id)

        # Check if already liked
        if Like.objects.is_liked_by(request.user, post):
            return Response(
                {"error": "You have already liked this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create like relationship
        with transaction.atomic():
            like, created = Like.objects.like_post(user=request.user, post=post)

        serializer = LikeSerializer(like, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def unlike_post(request, post_id):
    from posts.models import Post

    post = get_object_or_404(Post, pk=post_id)

    # Check if actually liked
    if not Like.objects.is_liked_by(request.user, post):
        return Response(
            {"error": "You have not liked this post."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Remove like relationship
    with transaction.atomic():
        success = Like.objects.unlike_post(user=request.user, post=post)

        if success:
            return Response({"message": "Post unliked successfully."})
        else:
            return Response(
                {"error": "Unable to unlike post."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PostLikesView(generics.ListAPIView):
    """
    List users who liked a specific post
    """

    serializer_class = PostLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get likes for the specified post"""
        post_id = self.kwargs.get("post_id")
        from posts.models import Post

        post = get_object_or_404(Post, pk=post_id)
        return Like.objects.for_post(post).with_post_and_user()


class UserLikesView(generics.ListAPIView):
    """
    List posts that a specific user has liked
    """

    serializer_class = UserLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        user = get_object_or_404(User, pk=user_id)
        return Like.objects.by_user(user).with_post_and_user()


class MyLikesView(generics.ListAPIView):
    """
    List posts that current user has liked
    """

    serializer_class = UserLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get posts liked by current user"""
        return Like.objects.by_user(self.request.user).with_post_and_user()


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def like_stats(request, user_id=None):
    """
    Get like statistics for a user
    """
    if user_id:
        target_user = get_object_or_404(User, pk=user_id)
    else:
        target_user = request.user

    total_likes_given = Like.objects.filter(user=target_user).count()

    total_likes_received = Like.objects.filter(post__user=target_user).count()

    most_liked_post = None
    user_posts = (
        Post.objects.filter(user=target_user)
        .annotate(total_likes=Count("likes"))
        .order_by("-total_likes")
        .first()
    )

    if user_posts and user_posts.total_likes > 0:
        most_liked_post = {
            "id": user_posts.id,
            "caption": user_posts.caption,
            "like_count": user_posts.total_likes,
            "created_at": user_posts.created_at,
        }

    # Recent likes given by user
    recent_likes = (
        Like.objects.filter(user=target_user)
        .select_related("post")
        .order_by("-created_at")[:5]
    )

    recent_likes_data = []
    for like in recent_likes:
        recent_likes_data.append(
            {
                "post_id": like.post.id,
                "post_caption": like.post.caption,
                "liked_at": like.created_at,
            }
        )

    stats = {
        "total_likes_given": total_likes_given,
        "total_likes_received": total_likes_received,
        "most_liked_post": most_liked_post,
        "recent_likes": recent_likes_data,
    }

    serializer = LikeStatsSerializer(stats)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def trending_posts(request):
    """
    Get trending posts based on recent likes
    """
    from posts.models import Post
    from django.utils import timezone
    from datetime import timedelta

    week_ago = timezone.now() - timedelta(days=7)

    trending = (
        Post.objects.annotate(
            recent_likes=Count(
                "likes", filter=models.Q(likes__created_at__gte=week_ago)
            ),
            total_likes=Count("likes"),
        )
        .filter(recent_likes__gt=0)
        .order_by("-recent_likes", "-total_likes")[:20]
    )

    from posts.serializers import PostListSerializer

    serializer = PostListSerializer(trending, many=True, context={"request": request})

    return Response(serializer.data)
