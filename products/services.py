from .mappers import CategoryMapper as mc
from .mappers import BrandMapper as mb
from .mappers import ProductMapper as mp
import json
from django.db import DatabaseError
from django.db import transaction
import base64
from .repository import Repository
from django.core.files.base import ContentFile
import os
import hashlib
from .messages import MessageTemplates
from django.conf import settings
from .parametervalidator import ParameterValidator
from django.http import JsonResponse
class CategoryService:
    def __init__(self, repository, cache_strategy):
        self.repository = repository
        self.cache_strategy = cache_strategy

    def get_categories(self, params):
        validator = ParameterValidator(params)
        params = validator.validate()
        if 'errors' in params:  # If validation failed, it will return a JsonResponse
            return params
        caching_params = params.copy()
        caching_params['entity'] = 'categories'
        cache_key = hashlib.md5(json.dumps(caching_params, sort_keys=True).encode()).hexdigest()
        cached_data = self.cache_strategy.get(cache_key)
        if cached_data:
            return cached_data
        mapper = mc()
        get_fields = mapper.get_allowed_fields()
        query = f"SELECT {get_fields} FROM products_category WHERE 1=1"
        query_params = []
        for key, value in params.items():
            if value:
                if key == 'name':
                    query += f" AND long_name LIKE %s OR short_name LIKE %s"
                    query_params.append(f'%{value}%')
                    query_params.append(f'%{value}%')
                elif key != 'page_size' and key != 'page':
                    query += f" AND {key} = %s"
                    query_params.append(value)
        if params['page_size'] and params['page']:
            offset = int(params['page_size']) * (int(params['page'])-1)
            query += f" ORDER BY short_name LIMIT {params['page_size']} OFFSET {offset}"
        categories = self.repository.fetch(query, query_params)
        self.cache_strategy.set(cache_key, categories, timeout=60 * 15)
        return categories

    def create_category(self, request):
        responses = []
        data = request.data
        if not isinstance(data, list):
            responses.append({'error': MessageTemplates.get_message("API_PAYLOAD_ERRROR", payload_type = type(data))})
            return responses, 400
        mapper = mc()
        with self.repository.connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        with transaction.atomic():
            try:
                for category in data:
                    data_db = mapper.convert_to_db(category)
                    validator = ParameterValidator(data_db)
                    data_db = validator.validate()
                    if 'errors' in data_db:
                        responses.append({'data': category,
                                          'error': data_db['errors']})
                        continue
                    mapper.validate_insert(data_db)
                    if self.repository.exists('category', data_db['category_id']):
                        responses.append({'data': category,
                                          'error': MessageTemplates.get_message('ID_EXISTS',entity_name = "Category", entity_id = data_db["category_id"])})
                        
                        continue
                    if 'image' in list(data_db.keys()):
                        data_db['image'] = self._save_image(data_db['image'], data_db['category_id'])
                    db_response = self.repository.insert('category',data_db)
                    if db_response == True:
                        responses.append({'data': category,
                                          'message': MessageTemplates.get_message('CREATED_SUCCESSFULLY',entity_name="Category",entity_id = data_db['category_id'])})
                    else:
                        return db_response,500
            except DatabaseError as db_error:
                transaction.set_rollback(True)
                return {'error': str(db_error)}, 500
            except ValueError as v:
                transaction.set_rollback(True)
                return {'error': str(v)}, 400
        return responses, 201
                

    def update_category(self, request):
        responses = []
        data = request.data
        if not isinstance(data, list):
            responses.append({'error': MessageTemplates.get_message("API_PAYLOAD_ERRROR", payload_type = type(data))})
            return responses, 400
        mapper = mc()
        with self.repository.connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        with transaction.atomic():
            try:
                for category in data:
                    data_db = mapper.convert_to_db(category)
                    mapper.validate_update(data_db)
                    validator = ParameterValidator(data_db)
                    data_db = validator.validate()
                    if 'errors' in data_db:
                        responses.append({'data': category,
                                          'error': data_db['errors']})
                        continue
                    if 'image' in list(data_db.keys()):
                        data_db['image'] = self._save_image(data_db['image'], data_db['category_id'])
                    category_id = data_db['category_id']  # Get the category ID for updating
                    if not self.repository.exists('category', category_id):
                        responses.append({'error': MessageTemplates.get_message("ID_NOT_EXISTS", entity_name = "Category", entity_id = category_id)})
                        continue
                    #columns = ', '.join([f"{col} = %s" for col in data_db.keys()])
                    values = list(data_db.values())
                    db_response = self.repository.update('category', data_db)
                    if db_response == True:
                        responses.append({'message': MessageTemplates.get_message("UPDATE_SUCCESS", entity_name = "Category", entity_id = data_db['category_id'])})
                    elif db_response == 'no change':
                        responses.append({'message': MessageTemplates.get_message("NO_CHANGE", entity_name = "Category", entity_id = data_db['category_id'])})
                    else:
                        return {'error':db_response}, 500
            except ValueError as v:
                transaction.set_rollback(True)
                return {'error': str(v)}, 400
            except DatabaseError as db_error:
                transaction.set_rollback(True)
                return {'error': str(db_error)}, 500
        return responses, 200
    
    def _save_image(self, image_data, category_id):
        try:
            image_storage_path = os.path.join(settings.MEDIA_ROOT, 'category')
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_file_name = f"{category_id}.{ext}"
            image_path = os.path.join(image_storage_path, image_file_name)
            with open(image_path, 'wb') as img_file:
                img_file.write(base64.b64decode(imgstr))
            return image_file_name
        except Exception as e:
            raise RuntimeError(f'Failed to save image for category ID {category_id}: {str(e)}')
        
class BrandService:
    def __init__(self, repository, cache_strategy):
        self.repository = repository
        self.cache_strategy = cache_strategy

    def get_brands(self, params):
        validator = ParameterValidator(params)
        params = validator.validate()
        if 'errors' in params:  # If validation failed, it will return a JsonResponse
            return params
        caching_params = params.copy()
        caching_params['entity'] = 'brands'
        cache_key = hashlib.md5(json.dumps(caching_params, sort_keys=True).encode()).hexdigest()
        cached_data = self.cache_strategy.get(cache_key)
        if cached_data:
            return cached_data
        mapper = mb()
        get_fields = mapper.get_allowed_fields()
        query = f"SELECT {get_fields} FROM products_brand WHERE 1=1"
        query_params = []
        for key, value in params.items():
            if value:
                if key == 'name':
                    query += f" AND name LIKE %s"
                    query_params.append(f'%{value}%')
                    query_params.append(f'%{value}%')
                elif key != 'page_size' and key != 'page':
                    query += f" AND {key} = %s"
                    query_params.append(value)
        if params['page_size'] and params['page']:
            offset = int(params['page_size']) * (int(params['page'])-1)
            query += f" ORDER BY name LIMIT {params['page_size']} OFFSET {offset}"
        brands = self.repository.fetch(query, query_params)
        self.cache_strategy.set(cache_key, brands, timeout=60 * 15)
        return brands

    def create_brand(self, request):
        responses = []
        data = request.data
        if not isinstance(data, list):
            responses.append({'error': MessageTemplates.get_message("API_PAYLOAD_ERRROR", payload_type = type(data))})
            return responses, 400
        mapper = mb()
        with self.repository.connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        with transaction.atomic():
            try:
                for brand in data:
                    data_db = mapper.convert_to_db(brand)
                    validator = ParameterValidator(data_db)
                    data_db = validator.validate()
                    if 'errors' in data_db:
                        responses.append({'data': brand,
                                          'error': data_db['errors']})
                        continue
                    mapper.validate_insert(data_db)
                    if self.repository.exists('brand', data_db['brand_id']):
                        responses.append({'data': brand,
                                          'error': MessageTemplates.get_message('ID_EXISTS',entity_name = "brand", entity_id = data_db["brand_id"])})
                        
                        continue
                    if 'image' in list(data_db.keys()):
                        data_db['image'] = self._save_image(data_db['image'], data_db['brand_id'])
                    db_response = self.repository.insert('brand',data_db)
                    if db_response == True:
                        responses.append({'data': brand,
                                          'message': MessageTemplates.get_message('CREATED_SUCCESSFULLY',entity_name="brand",entity_id = data_db['brand_id'])})
                    else:
                        return db_response,500
            except DatabaseError as db_error:
                transaction.set_rollback(True)
                return {'error': str(db_error)}, 500
            except ValueError as v:
                transaction.set_rollback(True)
                return {'error': str(v)}, 400
        return responses, 201
                

    def update_brand(self, request):
        responses = []
        data = request.data
        if not isinstance(data, list):
            responses.append({'error': MessageTemplates.get_message("API_PAYLOAD_ERRROR", payload_type = type(data))})
            return responses, 400
        mapper = mb()
        with self.repository.connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        with transaction.atomic():
            try:
                for brand in data:
                    data_db = mapper.convert_to_db(brand)
                    mapper.validate_update(data_db)
                    validator = ParameterValidator(data_db)
                    data_db = validator.validate()
                    if 'errors' in data_db:
                        responses.append({'data': brand,
                                          'error': data_db['errors']})
                        continue
                    if 'image' in list(data_db.keys()):
                        data_db['image'] = self._save_image(data_db['image'], data_db['brand_id'])
                    brand_id = data_db['brand_id']  # Get the brand ID for updating
                    if not self.repository.exists('brand', brand_id):
                        responses.append({'error': MessageTemplates.get_message("ID_NOT_EXISTS", entity_name = "brand", entity_id = brand_id)})
                        continue
                    #columns = ', '.join([f"{col} = %s" for col in data_db.keys()])
                    values = list(data_db.values())
                    db_response = self.repository.update('brand', data_db)
                    if db_response == True:
                        responses.append({'message': MessageTemplates.get_message("UPDATE_SUCCESS", entity_name = "brand", entity_id = data_db['brand_id'])})
                    elif db_response == 'no change':
                        responses.append({'message': MessageTemplates.get_message("NO_CHANGE", entity_name = "brand", entity_id = data_db['brand_id'])})
                    else:
                        return {'error':db_response}, 500
            except ValueError as v:
                transaction.set_rollback(True)
                return {'error': str(v)}, 400
            except DatabaseError as db_error:
                transaction.set_rollback(True)
                return {'error': str(db_error)}, 500
        return responses, 200
    
    def _save_image(self, image_data, brand_id):
        try:
            image_storage_path = os.path.join(settings.MEDIA_ROOT, 'brand')
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_file_name = f"{brand_id}.{ext}"
            image_path = os.path.join(image_storage_path, image_file_name)
            with open(image_path, 'wb') as img_file:
                img_file.write(base64.b64decode(imgstr))
            return image_file_name
        except Exception as e:
            raise RuntimeError(f'Failed to save image for brand ID {brand_id}: {str(e)}')


class ProductService:
    def __init__(self, repository, cache_strategy):
        self.repository = repository
        self.cache_strategy = cache_strategy

    def get_products(self, params):
        validator = ParameterValidator(params)
        params = validator.validate()
        if 'errors' in params:  # If validation failed, it will return a JsonResponse
            return params
        caching_params = params.copy()
        caching_params['entity'] = 'products'
        cache_key = hashlib.md5(json.dumps(caching_params, sort_keys=True).encode()).hexdigest()
        cached_data = self.cache_strategy.get(cache_key)
        if cached_data:
            return cached_data
        mapper = mp()
        get_fields = mapper.get_allowed_fields()
        query = f"SELECT {get_fields} FROM products_product WHERE 1=1"
        query_params = []
        for key, value in params.items():
            if value:
                if key == 'name':
                    query += f" AND long_name LIKE %s OR short_name LIKE %s"
                    query_params.append(f'%{value}%')
                    query_params.append(f'%{value}%')
                elif key != 'page_size' and key != 'page':
                    query += f" AND {key} = %s"
                    query_params.append(value)
        if params['page_size'] and params['page']:
            offset = int(params['page_size']) * (int(params['page'])-1)
            query += f" ORDER BY product_name LIMIT {params['page_size']} OFFSET {offset}"
        products = self.repository.fetch(query, query_params)
        self.cache_strategy.set(cache_key, products, timeout=60 * 15)
        return products

    def create_product(self, request):
        responses = []
        data = request.data
        if not isinstance(data, list):
            responses.append({'error': MessageTemplates.get_message("API_PAYLOAD_ERRROR", payload_type = type(data))})
            return responses, 400
        mapper = mc()
        with self.repository.connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        with transaction.atomic():
            try:
                for product in data:
                    data_db = mapper.convert_to_db(product)
                    validator = ParameterValidator(data_db)
                    data_db = validator.validate()
                    if 'errors' in data_db:
                        responses.append({'data': product,
                                          'error': data_db['errors']})
                        continue
                    mapper.validate_insert(data_db)
                    if self.repository.exists('product', data_db['product_id']):
                        responses.append({'data': product,
                                          'error': MessageTemplates.get_message('ID_EXISTS',entity_name = "product", entity_id = data_db["product_id"])})
                        
                        continue
                    if 'image' in list(data_db.keys()):
                        data_db['image'] = self._save_image(data_db['image'], data_db['product_id'])
                    db_response = self.repository.insert('product',data_db)
                    if db_response == True:
                        responses.append({'data': product,
                                          'message': MessageTemplates.get_message('CREATED_SUCCESSFULLY',entity_name="product",entity_id = data_db['product_id'])})
                    else:
                        return db_response,500
            except DatabaseError as db_error:
                transaction.set_rollback(True)
                return {'error': str(db_error)}, 500
            except ValueError as v:
                transaction.set_rollback(True)
                return {'error': str(v)}, 400
        return responses, 201
                

    def update_product(self, request):
        responses = []
        data = request.data
        if not isinstance(data, list):
            responses.append({'error': MessageTemplates.get_message("API_PAYLOAD_ERRROR", payload_type = type(data))})
            return responses, 400
        mapper = mp()
        with self.repository.connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        with transaction.atomic():
            try:
                for product in data:
                    data_db = mapper.convert_to_db(product)
                    mapper.validate_update(data_db)
                    validator = ParameterValidator(data_db)
                    data_db = validator.validate()
                    if 'errors' in data_db:
                        responses.append({'data': product,
                                          'error': data_db['errors']})
                        continue
                    if 'image' in list(data_db.keys()):
                        data_db['image'] = self._save_image(data_db['image'], data_db['product_id'])
                    product_id = data_db['product_id']  # Get the product ID for updating
                    if not self.repository.exists('product', product_id):
                        responses.append({'error': MessageTemplates.get_message("ID_NOT_EXISTS", entity_name = "product", entity_id = product_id)})
                        continue
                    #columns = ', '.join([f"{col} = %s" for col in data_db.keys()])
                    values = list(data_db.values())
                    db_response = self.repository.update('product', data_db)
                    if db_response == True:
                        responses.append({'message': MessageTemplates.get_message("UPDATE_SUCCESS", entity_name = "product", entity_id = data_db['product_id'])})
                    elif db_response == 'no change':
                        responses.append({'message': MessageTemplates.get_message("NO_CHANGE", entity_name = "product", entity_id = data_db['product_id'])})
                    else:
                        return {'error':db_response}, 500
            except ValueError as v:
                transaction.set_rollback(True)
                return {'error': str(v)}, 400
            except DatabaseError as db_error:
                transaction.set_rollback(True)
                return {'error': str(db_error)}, 500
        return responses, 200
    
    def _save_image(self, image_data, product_id):
        try:
            image_storage_path = os.path.join(settings.MEDIA_ROOT, 'product')
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_file_name = f"{product_id}.{ext}"
            image_path = os.path.join(image_storage_path, image_file_name)
            with open(image_path, 'wb') as img_file:
                img_file.write(base64.b64decode(imgstr))
            return image_file_name
        except Exception as e:
            raise RuntimeError(f'Failed to save image for product ID {product_id}: {str(e)}')