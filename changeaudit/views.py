from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.db import transaction,DatabaseError
from rest_framework.response import Response
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from django.views import View
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import HasAccessPermission
from .services import CategoryService
from .cache import CacheStrategy
from .repository import Repository
from django.db import connection
from rest_framework.views import APIView
from .middleware import RequestStore
from .serializers import get_authenticated_user,has_edit_access,has_create_access
import json
import logging
import time
from .mappers import ProductMapper as mp
from .mappers import BrandMapper as mb

class ChangeHistory(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasAccessPermission]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache_strategy = CacheStrategy(cache)
        self.category_service = CategoryService(Repository(connection), self.cache_strategy)
        self.response = {}

    def get(self, request, *args, **kwargs):
        params = {
            'category_id': request.GET.get('id'),
            'name': request.GET.get('name'),
            'status': request.GET.get('status'),
            'created_by': request.GET.get('created_by')
        }
        categories = self.category_service.get_categories(params)
        if not categories:
            return JsonResponse({'error': 'No categories found matching the criteria'}, status=404)
        self.responseParser(request, categories)
        return Response(self.response, status=200)

    def post(self, request, *args, **kwargs):
        RequestStore.set_request_headers(request.headers)
        response, status_code = self.category_service.create_category(request)
        self.responseParser(request, response)
        return Response(self.response, status=status_code)

    def put(self, request, *args, **kwargs):
        response, status_code = self.category_service.update_category(request)
        self.responseParser(request, response)
        return Response(self.response, status=status_code)

    def delete(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['DELETE'])
    
    def responseParser(self, request, data):
        query_params = request.query_params.dict()
        path_vars = request.parser_context['kwargs']
        if request.headers:
            headers = {key: value for key, value in request.headers.items()}
        # Create a structured JSON response
        self.response = {
            'method': request.method,
            'path': request.path,
            'query_params': query_params,
            'path_variables': path_vars,
            'headers': headers,
            'results': data,
            'metadata': {
                'Count': len(data),
                'Timestamp': str(time.time()),
                'Pages': 1,
                'Page Size': 10
            }
        }
        if request.body:
            self.response['body'] = json.loads(request.body)