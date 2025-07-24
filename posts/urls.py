from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Post CRUD endpoints
    path('', views.PostListCreateView.as_view(), name='post-list-create'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    
    # Feed endpoints
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('timeline/', views.TimelineView.as_view(), name='timeline'),
    path('discover/', views.DiscoverView.as_view(), name='discover'),
    
    # Special post views
    path('popular/', views.PopularPostsView.as_view(), name='popular-posts'),
    path('my-posts/', views.my_posts, name='my-posts'),
    path('user/<int:user_id>/', views.UserPostsView.as_view(), name='user-posts'),
    
    # Statistics
    path('stats/', views.post_stats, name='post-stats'),
    path('feed-stats/', views.feed_stats, name='feed-stats'),
]
