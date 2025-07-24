from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Follow
from users.serializers import UserListSerializer

User = get_user_model()


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow model"""
    follower = UserListSerializer(read_only=True)
    following = UserListSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'created_at']


class FollowCreateSerializer(serializers.Serializer):
    """Serializer for creating follows"""
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        """Validate that the user exists"""
        try:
            user = User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        
        # Check if trying to follow self
        request = self.context.get('request')
        if request and request.user.pk == value:
            raise serializers.ValidationError("You cannot follow yourself.")
        
        return value
    
    def create(self, validated_data):
        """Create a follow relationship"""
        request = self.context.get('request')
        following_user = User.objects.get(pk=validated_data['user_id'])
        
        follow, created = Follow.objects.follow_user(
            follower=request.user,
            following=following_user
        )
        
        if not created:
            raise serializers.ValidationError("You are already following this user.")
        
        return follow


class FollowerListSerializer(serializers.ModelSerializer):
    """Serializer for listing followers"""
    follower = UserListSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['follower', 'created_at']


class FollowingListSerializer(serializers.ModelSerializer):
    """Serializer for listing following"""
    following = UserListSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['following', 'created_at']


class FollowStatsSerializer(serializers.Serializer):
    """Serializer for follow statistics"""
    followers_count = serializers.IntegerField()
    following_count = serializers.IntegerField()
    is_following = serializers.BooleanField()
    is_followed_by = serializers.BooleanField()
    mutual_follows = serializers.IntegerField()


from .models import Like
from posts.serializers import PostListSerializer


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for Like model"""
    user = UserListSerializer(read_only=True)
    post = PostListSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']


class LikeCreateSerializer(serializers.Serializer):
    """Serializer for creating likes"""
    post_id = serializers.IntegerField()
    
    def validate_post_id(self, value):
        """Validate that the post exists"""
        from posts.models import Post
        try:
            post = Post.objects.get(pk=value)
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post not found.")
        
        return value
    
    def create(self, validated_data):
        """Create a like relationship"""
        from posts.models import Post
        request = self.context.get('request')
        post = Post.objects.get(pk=validated_data['post_id'])
        
        like, created = Like.objects.like_post(
            user=request.user,
            post=post
        )
        
        if not created:
            raise serializers.ValidationError("You have already liked this post.")
        
        return like


class PostLikeSerializer(serializers.ModelSerializer):
    """Serializer for showing who liked a post"""
    user = UserListSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['user', 'created_at']


class UserLikeSerializer(serializers.ModelSerializer):
    """Serializer for showing posts a user liked"""
    post = PostListSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['post', 'created_at']


class LikeStatsSerializer(serializers.Serializer):
    """Serializer for like statistics"""
    total_likes_given = serializers.IntegerField()
    total_likes_received = serializers.IntegerField()
    most_liked_post = serializers.DictField(allow_null=True)
    recent_likes = serializers.ListField()
