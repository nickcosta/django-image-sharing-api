from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    # read-only for everyone, write for owner only
    
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        return obj == request.user


class IsOwnerOnly(BasePermission):
    # owner access only
    
    def has_object_permission(self, request, view, obj):
        return obj == request.user
