# permissions.py
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication


class HasAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get role-based access from JWT token
        access = request.auth.payload
        method = request.method.upper()
        # Define access levels for different methods
        access_levels = {
            'GET': 'VIEW',
            'POST': 'VIEW',
            'PUT': 'VIEW',
            'DELETE': 'VIEW'
        }
        access_hierarchy = {
        'VIEW': 1,
        'EDIT': 2,
        'CREATE': 3,
        'DELETE': 3
    }
        
        required_access = access_levels[method]
        user_access_level = access.get("cart_access")
        if access_hierarchy[user_access_level] <  access_hierarchy[required_access]:
            return False      
        return True
