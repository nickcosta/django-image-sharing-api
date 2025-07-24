from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    # User management endpoints
    path('', views.UserListView.as_view(), name='user-list'),
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
    path('<str:pk>/', views.UserDetailView.as_view(), name='user-detail'),
]
