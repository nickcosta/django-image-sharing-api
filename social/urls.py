from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # Follow/Unfollow actions
    path('follow/<int:user_id>/', views.follow_user, name='follow-user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow-user'),
    
    # User followers/following lists
    path('users/<int:user_id>/followers/', views.UserFollowersView.as_view(), name='user-followers'),
    path('users/<int:user_id>/following/', views.UserFollowingView.as_view(), name='user-following'),
    
    # Current user followers/following
    path('my-followers/', views.MyFollowersView.as_view(), name='my-followers'),
    path('my-following/', views.MyFollowingView.as_view(), name='my-following'),
    
    # Like/Unlike actions
    path('like/<int:post_id>/', views.like_post, name='like-post'),
    path('unlike/<int:post_id>/', views.unlike_post, name='unlike-post'),
    
    # Post likes and user likes
    path('posts/<int:post_id>/likes/', views.PostLikesView.as_view(), name='post-likes'),
    path('users/<int:user_id>/likes/', views.UserLikesView.as_view(), name='user-likes'),
    path('my-likes/', views.MyLikesView.as_view(), name='my-likes'),
    
    # Statistics and trending
    path('stats/', views.follow_stats, name='follow-stats'),
    path('stats/<int:user_id>/', views.follow_stats, name='user-follow-stats'),
    path('like-stats/', views.like_stats, name='like-stats'),
    path('like-stats/<int:user_id>/', views.like_stats, name='user-like-stats'),
    path('suggested/', views.suggested_users, name='suggested-users'),
    path('mutual/<int:user_id>/', views.mutual_follows, name='mutual-follows'),
    path('trending/', views.trending_posts, name='trending-posts'),
]
