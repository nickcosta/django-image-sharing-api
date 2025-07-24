from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from social.models import Follow, Like
from posts.models import Post
import uuid

User = get_user_model()

class FollowTests(APITestCase):
    """Test follow functionality"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test users with unique emails
        unique_id = str(uuid.uuid4())[:8]
        self.user1 = User.objects.create_user(
            username=f'user1_{unique_id}', 
            email=f'user1_{unique_id}@example.com',
            password='test123'
        )
        self.user2 = User.objects.create_user(
            username=f'user2_{unique_id}', 
            email=f'user2_{unique_id}@example.com',
            password='test123'
        )
        
        self.token1 = Token.objects.create(user=self.user1)
    
    def test_follow_user(self):
        """Test user can follow another user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.post(f'/api/v1/social/follow/{self.user2.pk}/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify follow relationship was created
        follow = Follow.objects.get(follower=self.user1, following=self.user2)
        self.assertIsNotNone(follow)
    
    def test_get_my_following(self):
        """Test getting users current user follows"""
        # Create follow relationship
        Follow.objects.create(follower=self.user1, following=self.user2)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.get('/api/v1/social/my-following/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle pagination
        if 'results' in response.data:
            self.assertGreaterEqual(len(response.data['results']), 1)
        else:
            self.assertGreaterEqual(len(response.data), 1)


class LikeTests(APITestCase):
    """Test like functionality"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test users with unique emails
        unique_id = str(uuid.uuid4())[:8]
        self.user1 = User.objects.create_user(
            username=f'user1_{unique_id}', 
            email=f'user1_{unique_id}@example.com',
            password='test123'
        )
        self.user2 = User.objects.create_user(
            username=f'user2_{unique_id}', 
            email=f'user2_{unique_id}@example.com',
            password='test123'
        )
        
        self.token1 = Token.objects.create(user=self.user1)
        
        # Create test post
        self.post = Post.objects.create(
            user=self.user2,
            caption='Test post',
            image_url='https://picsum.photos/400/400?random=1'
        )
    
    def test_like_post(self):
        """Test user can like a post"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.post(f'/api/v1/social/like/{self.post.pk}/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify like was created
        like = Like.objects.get(user=self.user1, post=self.post)
        self.assertIsNotNone(like)
    
    def test_get_my_likes(self):
        """Test getting current user's likes"""
        # Create like
        Like.objects.create(user=self.user1, post=self.post)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.get('/api/v1/social/my-likes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle pagination
        if 'results' in response.data:
            self.assertGreaterEqual(len(response.data['results']), 1)
        else:
            self.assertGreaterEqual(len(response.data), 1)
