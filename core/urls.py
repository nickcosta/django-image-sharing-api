from django.urls import path, include

app_name = 'core'

urlpatterns = [
    path('users/', include('users.urls')),
    path('posts/', include('posts.urls')),
    path('social/', include('social.urls')),
]
