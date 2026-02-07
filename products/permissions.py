from rest_framework.permissions import BasePermission
from abc import ABC, abstractmethod
from .middleware import RequestStore
import logging
from django.conf import settings
logger = logging.getLogger(__name__)
class AccessLevelStrategy(ABC):
    @abstractmethod
    def get_required_access(self, method: str) -> str:
        pass
    @abstractmethod
    def check_access(self, user_access: str, required_access: str) -> bool:
        pass


class DefaultAccessLevelStrategy(AccessLevelStrategy):
    access_levels = settings.ACCESS_LEVELS
    access_hierarchy = settings.ACCESS_HIERARCHY

    def get_required_access(self, method: str) -> str:
        return self.access_levels.get(method.upper(), 'VIEW')
    
    def check_access(self, user_access: str, required_access: str) -> bool:
        """Check if user's access level is sufficient for the requested method."""
        return self.access_hierarchy.get(user_access, 0) >= self.access_hierarchy.get(required_access, 0)


class HasAccessPermission(BasePermission):

    def __init__(self, strategy: AccessLevelStrategy = None):
        # Use dependency injection to allow for different access strategies
        self.strategy = strategy or DefaultAccessLevelStrategy()

    def has_permission(self, request, view):
        if request.method not in ['GET']: #no authentication required for get request
            if not request.user.is_authenticated:
                return False
            access = request.auth.payload.get("product_access")
            RequestStore.set_access_level(access)
            if not access:
                print("No access level provided in the JWT token")
                return False
            method = request.method.upper()
            required_access = self.strategy.get_required_access(method)
            if not self.strategy.check_access(access, required_access):
                print(f"Insufficient access: required {required_access}, but user has {access}")
                return False
            self.log_access_attempt(request, required_access, access)
            return True
        else:
            if hasattr(request, 'auth') and request.auth is not None:
                RequestStore.set_access_level(request.auth.payload.get("product_access"))
            else:
                RequestStore.set_access_level(None)
            return True

    def log_access_attempt(self, request, required_access, user_access):
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        logger.info(f"User '{user}' attempted to access '{request.path}' "
                    f"with method '{request.method}', required '{required_access}', "
                    f"and user has '{user_access}' access level.")
