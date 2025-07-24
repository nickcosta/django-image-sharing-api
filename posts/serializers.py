from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post
from .validators import validate_caption_length, validate_image_url_format
from users.serializers import UserListSerializer

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating posts"""
    user = UserListSerializer(read_only=True)
    total_likes = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'caption', 'image_url', 
            'total_likes', 'is_liked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_total_likes(self, obj):
        """Get the number of likes for this post"""
        if hasattr(obj, 'total_likes'):
            # If annotated in queryset
            return obj.total_likes
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        """Check if current user liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False
    
    def validate_caption(self, value):
        """Validate caption"""
        validate_caption_length(value)
        return value.strip()
    
    def validate_image_url(self, value):
        """Validate image URL"""
        validate_image_url_format(value)
        return value
    
    def create(self, validated_data):
        """Create post with current user"""
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    total_likes = serializers.IntegerField(read_only=True)
    total_likes = serializers.IntegerField(read_only=True)
    total_likes = serializers.IntegerField(read_only=True)
    """Lightweight serializer for post lists"""
    user = UserListSerializer(read_only=True)
    total_likes = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'caption', 'image_url', 
            'total_likes', 'is_liked', 'created_at'
        ]
    
    def get_total_likes(self, obj):
        """Get the number of likes for this post"""
        if hasattr(obj, 'total_likes'):
            return obj.total_likes
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        """Check if current user liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False


class PostDetailSerializer(PostSerializer):
    """Detailed serializer for individual post views"""
    pass  # Same as PostSerializer for now, can be extended later


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer specifically for creating posts"""
    
    class Meta:
        model = Post
        fields = ['caption', 'image_url']
    
    def validate_caption(self, value):
        """Validate caption"""
        validate_caption_length(value)
        return value.strip()
    
    def validate_image_url(self, value):
        """Validate image URL"""
        validate_image_url_format(value)
        return value
    
    def create(self, validated_data):
        """Create post with current user"""
        request = self.context.get('request')
        validated_data['user'] = request.user
        return Post.objects.create(**validated_data)
