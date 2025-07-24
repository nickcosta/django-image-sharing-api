from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
import uuid

User = get_user_model()

class UserAuthenticationTests(APITestCase):
    """Test authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/users/register/'
        self.login_url = '/api/v1/users/login/'
        self.logout_url = '/api/v1/users/logout/'
        
        # Unique test user data
        unique_id = str(uuid.uuid4())[:8]
        self.user_data = {
            'username': f'testuser_{unique_id}',
            'email': f'test_{unique_id}@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_registration(self):
        """Test user can register successfully"""
        response = self.client.post(
            self.register_url, 
            self.user_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        
        # Verify user was created in database
        user = User.objects.get(username=self.user_data['username'])
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_login(self):
        """Test user can login successfully"""
        # Create user first with unique data
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
        
        login_data = {
            'username': user.username,
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
    
    def test_get_current_user(self):
        """Test user can get their own profile"""
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
        token = Token.objects.create(user=user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get('/api/v1/users/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], user.username)


class UserListTests(APITestCase):
    """Test user listing endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test users with unique emails
        unique_id = str(uuid.uuid4())[:8]
        self.user1 = User.objects.create_user(
            username=f'user1_{unique_id}',
            email=f'user1_{unique_id}@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username=f'user2_{unique_id}',
            email=f'user2_{unique_id}@example.com',
            password='testpass123'
        )
        
        self.token1 = Token.objects.create(user=self.user1)
    
    def test_get_user_list_authenticated(self):
        """Test authenticated user can get user list"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.get('/api/v1/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_get_user_list_unauthenticated(self):
        """Test unauthenticated user cannot access user list"""
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
