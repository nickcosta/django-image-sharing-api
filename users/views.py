from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import UserProfile
from .serializers import (
    UserSerializer, UserListSerializer, UserDetailSerializer
)
from .permissions import IsOwnerOrReadOnly, IsOwnerOnly

User = get_user_model()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """
    Register a new user and return authentication token
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'user': UserDetailSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """
    Authenticate user and return token
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserDetailSerializer(user).data,
            'token': token.key
        })
    
    return Response({
        'error': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """
    Logout user by deleting their token
    """
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'})
    except Token.DoesNotExist:
        return Response({'error': 'User was not logged in'}, 
                       status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """
    List all users with optimized queries
    """
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Optimized queryset with select_related for profile"""
        return User.objects.select_related('profile').order_by('username')


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update user details
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        """Optimized queryset with select_related for profile"""
        return User.objects.select_related('profile')
    
    def get_object(self):
        """Get user by ID or username"""
        lookup_value = self.kwargs.get('pk')
        
        if lookup_value.isdigit():
            return get_object_or_404(self.get_queryset(), pk=lookup_value)
        else:
            return get_object_or_404(self.get_queryset(), username=lookup_value)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update current user's profile
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Return current user with profile"""
        user = User.objects.select_related('profile').get(pk=self.request.user.pk)
        return user
