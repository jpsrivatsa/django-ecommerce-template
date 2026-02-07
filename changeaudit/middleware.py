from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import json
from .serializers import get_authenticated_user
class RequestStore:
    _request_header = None
    _request_user = None
    @classmethod
    def set_request_headers(cls, headers):
        cls._request_header = headers
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
    
class RequestHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request headers in RequestStore
        RequestStore.set_request_headers(request.headers)
        response = self.get_response(request)
        return response
    
