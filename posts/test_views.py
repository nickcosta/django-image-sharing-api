from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from posts.models import Post
import uuid

User = get_user_model()

class PostCRUDTests(APITestCase):
    """Test basic post operations"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test user with unique email
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
        
        self.token = Token.objects.create(user=self.user)
        
        # Valid post data
        self.valid_post_data = {
            'caption': 'Test post caption',
            'image_url': 'https://picsum.photos/400/400?random=1'
        }
    
    def test_create_post_authenticated(self):
        """Test authenticated user can create post"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post('/api/v1/posts/', self.valid_post_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['caption'], 'Test post caption')
        # Check if post was created
        self.assertTrue(Post.objects.filter(caption='Test post caption').exists())
    
    def test_create_post_unauthenticated(self):
        """Test unauthenticated user cannot create post"""
        response = self.client.post('/api/v1/posts/', self.valid_post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_posts(self):
        """Test user can list posts"""
        # Create a post first
        Post.objects.create(
            user=self.user,
            caption='Test post',
            image_url='https://picsum.photos/400/400?random=1'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/v1/posts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle pagination
        if 'results' in response.data:
            self.assertGreaterEqual(len(response.data['results']), 1)
        else:
            # If not paginated
            self.assertGreaterEqual(len(response.data), 1)
    
    def test_get_my_posts(self):
        """Test my posts endpoint"""
        Post.objects.create(
            user=self.user,
            caption='My post',
            image_url='https://picsum.photos/400/400?random=1'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/v1/posts/my-posts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle pagination
        if 'results' in response.data:
            self.assertGreaterEqual(len(response.data['results']), 1)
        else:
            self.assertGreaterEqual(len(response.data), 1)

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Post
from social.models import Like

User = get_user_model()

class PopularPostsTests(APITestCase):
    def setUp(self):
        self.u = User.objects.create_user(username='popuser', email='popuser@example.com', password='pop_pw')
        self.client.login(username='popuser', password='pop_pw')
        self.client.force_authenticate(user=self.u)
        self.client.force_authenticate(user=self.u)
        p1 = Post.objects.create(user=self.u, caption='First', image_url='https://example.com/image.jpg')
        p2 = Post.objects.create(user=self.u, caption='Second', image_url='https://example.com/image.jpg')
        Like.objects.create(user=self.u, post=p1)
        Like.objects.create(user=self.u, post=p2)
        other = User.objects.create_user(username='other', email='other@example.com', password='other_pw')
        Like.objects.create(user=other, post=p2)

    def test_popular_endpoint(self):
        self.client.force_authenticate(user=self.u)
        url = '/api/v1/posts/popular/'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.status_code, 200)
        data = res.data['results'] if isinstance(res.data, dict) and 'results' in res.data else res.data
        ids = [post['id'] for post in data]
        like_map = {p['id']: p['total_likes'] for p in data}
        self.assertGreaterEqual(like_map[ids[0]], like_map[ids[-1]])
