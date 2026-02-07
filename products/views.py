from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.db import transaction,DatabaseError
from rest_framework.response import Response
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from django.views import View
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import HasAccessPermission
from .repsponseparser import ResponseParser
from .services import ProductService
from .services import CategoryService
from .services import BrandService
from .cache import CacheStrategy
from .repository import Repository
from django.db import connection
from rest_framework.views import APIView
from .middleware import RequestStore
from .messages import MessageTemplates
from .serializers import get_authenticated_user,has_edit_access,has_create_access
import json
import logging
import time
from .mappers import ProductMapper as mp
from .mappers import BrandMapper as mb
from django.conf import settings
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
logger = logging.getLogger(__name__)
class ProductView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasAccessPermission]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache_strategy = CacheStrategy(cache)
        self.product_service = ProductService(Repository(connection), self.cache_strategy)
        self.response = {}

    def get(self, request, *args, **kwargs):
        params = {
            'product_id': request.GET.get('id'),
            'name': request.GET.get('name'),
            'status': request.GET.get('status'),
            'created_by': request.GET.get('created_by'),
            'page_size' : request.GET.get('page_size'),
            'page': request.GET.get('page')
        }
        products = self.product_service.get_products(params)
        if not products:
            self.response = ResponseParser.parse_response(request, products, entity="products")
            return JsonResponse(self.response, status=404)
        if 'errors' in products:
            self.response = ResponseParser.parse_response(request, products, entity="products")
            return JsonResponse(self.response, status=404)
        for product in products: 
            image_name = product['product_id'] + '.jpeg'
            image_url = f"{settings.MEDIA_URL}product/{image_name}"
            product['image_url'] = request.build_absolute_uri(image_url)
        self.response = ResponseParser.parse_response(request, products, entity="products")
        return Response(self.response, status=200)

    def post(self, request, *args, **kwargs):
        RequestStore.set_request_headers(request.headers)
        response, status_code = self.product_service.create_product(request)
        self.response = ResponseParser.parse_response(request, response, entity="products")
        return Response(self.response, status=status_code)

    def put(self, request, *args, **kwargs):
        response, status_code = self.product_service.update_product(request)
        self.response = ResponseParser.parse_response(request, response, entity="products")
        return Response(self.response, status=status_code)

    def delete(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['DELETE'])
    
class CategoryView(APIView):
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
            'created_by': request.GET.get('created_by'),
            'page_size' : request.GET.get('page_size'),
            'page': request.GET.get('page')
        }
        categories = self.category_service.get_categories(params)
        if not categories:
            self.response = ResponseParser.parse_response(request, categories, entity="Categories")
            return JsonResponse(self.response, status=404)
        if 'errors' in categories:
            self.response = ResponseParser.parse_response(request, categories, entity="Categories")
            return JsonResponse(self.response, status=404)
        for category in categories: 
            image_name = category['category_id'] + '.jpeg'
            image_url = f"{settings.MEDIA_URL}category/{image_name}"
            category['image_url'] = request.build_absolute_uri(image_url)
        self.response = ResponseParser.parse_response(request, categories, entity="Categories")
        return Response(self.response, status=200)

    def post(self, request, *args, **kwargs):
        RequestStore.set_request_headers(request.headers)
        response, status_code = self.category_service.create_category(request)
        self.response = ResponseParser.parse_response(request, response, entity="Categories")
        return Response(self.response, status=status_code)

    def put(self, request, *args, **kwargs):
        response, status_code = self.category_service.update_category(request)
        self.response = ResponseParser.parse_response(request, response, entity="Categories")
        return Response(self.response, status=status_code)

    def delete(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['DELETE'])
    
    

    
class BrandView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasAccessPermission]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache_strategy = CacheStrategy(cache)
        self.brand_service = BrandService(Repository(connection), self.cache_strategy)
        self.response = {}

    def get(self, request, *args, **kwargs):
        params = {
            'brand_id': request.GET.get('id'),
            'name': request.GET.get('name'),
            'status': request.GET.get('status'),
            'created_by': request.GET.get('created_by'),
            'page_size' : request.GET.get('page_size'),
            'page': request.GET.get('page')
        }
        brands = self.brand_service.get_brands(params)
        if not brands:
            self.response = ResponseParser.parse_response(request, brands, entity="Brands")
            return JsonResponse(self.response, status=404)
        if 'errors' in brands:
            self.response = ResponseParser.parse_response(request, brands, entity="Brands")
            return JsonResponse(self.response, status=404)
        for brand in brands: 
            image_name = brand['brand_id'] + '.jpeg'
            image_url = f"{settings.MEDIA_URL}brand/{image_name}"
            brand['image_url'] = request.build_absolute_uri(image_url)
        self.response = ResponseParser.parse_response(request, brands, entity="Brands")
        return Response(self.response, status=200)

    def post(self, request, *args, **kwargs):
        RequestStore.set_request_headers(request.headers)
        response, status_code = self.brand_service.create_brand(request)
        self.response = ResponseParser.parse_response(request, response, entity="Brands")
        return Response(self.response, status=status_code)

    def put(self, request, *args, **kwargs):
        response, status_code = self.brand_service.update_brand(request)
        self.response = ResponseParser.parse_response(request, response, entity="Brands")
        return Response(self.response, status=status_code)

    def delete(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['DELETE'])