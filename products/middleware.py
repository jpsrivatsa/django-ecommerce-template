from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import json
from .serializers import get_authenticated_user
class RequestStore:
    _request_header = None
    _request_user = None
    _request_IP = None
    _access_level = None
    @classmethod
    def set_request_headers(cls, headers, ip = None):
        cls._request_header = headers
        cls._request_IP = ip
        try:
            cls._request_user = get_authenticated_user(headers)
        except AuthenticationFailed as e:
            return Response({'error': str(e)},status=401)
        
    @classmethod
    def get_request_headers(cls):
        return cls._request_header
    
    @classmethod
    def get_requested_user(cls):
        return cls._request_user
    
    @classmethod
    def set_access_level(cls, access_level):
        cls._access_level = access_level
        
    @classmethod
    def get_access_level(cls):
        return cls._access_level
        
    
    
    
class RequestHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request headers in RequestStore
        ip = request.META.get('REMOTE_ADDR ')
        RequestStore.set_request_headers(request.headers, ip)
        response = self.get_response(request)
        return response
    
