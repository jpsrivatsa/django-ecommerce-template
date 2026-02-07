from rest_framework import permissions
from .models import Admin

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return Admin.objects.filter(user=request.user).exists()
