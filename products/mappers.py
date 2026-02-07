from django.apps import apps
from django.core.exceptions import ValidationError
from .middleware import RequestStore
from .messages import MessageTemplates
import logging
from django.db import connection
from .repository import Repository
logger = logging.getLogger(__name__)
class ProductMapper:
    def __init__(self):
        self.field_mapping = {
            'id': 'product_id',
            'name': 'product_name',
            'category': 'category_id',
            'brand': 'brand_id',
            'vendor': 'vendor',
        }
        self.get_fields = ['product_id', 'product_name', 'category_id', 'brand_id']
    def get_required_fields(self):
        required_fields = [
            'product_id', 'product_name', 'category_id', 'brand_id', 'vendor'
        ]
        return required_fields 
    def convert_to_db(self,data):
        converted_data = {}
        for param, value in data.items():
            if param in self.field_mapping:
                db_field = self.field_mapping[param]
                converted_data[db_field] = value
            else:
                logger.warning(f'Unexpected parameter: {param}')
        return converted_data
    
    def get_required_fields_for_ud(self):
        required_fields = [
            'product_id'
        ]
        return required_fields
    
    def validate_insert(self, data):
        required_fields = self.get_required_fields()
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            raise ValueError(MessageTemplates.get_message("REQUIRED_FIELDS_MISSING", missing_fields = ', '.join(missing_fields)))
        return True

    def get_allowed_fields(self):
        if RequestStore.get_access_level() == 'VIEW' or RequestStore.get_access_level() is None:
            return ", ".join(self.get_fields)
        else:
            return '*'
    
    def validate_update(self, data):
        required_fields = self.get_required_fields_for_ud()
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            raise ValueError(MessageTemplates.get_message("REQUIRED_FIELDS_MISSING", missing_fields = ', '.join(missing_fields)))
        return True
    
class BrandMapper:
    def __init__(self):
        self.field_mapping = {
            'id': 'brand_id',
            'name': 'name',
            'logo': 'logo',
            'description': 'description',
            'website': 'website',
            'country':'country',
            'founded':'founded_year',
            'active':'is_active',
        }
        self.get_fields = ['brand_id', 'name', 'logo', 'description','website','country','founded']
    def get_required_fields(self):
        required_fields = [
            'brand_id', 'logo', 'name', 'description', 'website', 'country', 'founded_year', 'is_active'
        ]
        return required_fields 
    def convert_to_db(self,data):
        converted_data = {}
        for param, value in data.items():
            if param in self.field_mapping:
                db_field = self.field_mapping[param]
                converted_data[db_field] = value
            else:
                logger.warning(f'Unexpected parameter: {param}')
        return converted_data
    def get_allowed_fields(self):
        if RequestStore.get_access_level() == 'VIEW' or RequestStore.get_access_level() is None:
            return ", ".join(self.get_fields)
        else:
            return '*'
        
    def get_required_fields_for_ud(self):
        required_fields = [
            'brand_id'
        ]
        return required_fields
    
    def validate_insert(self, data):
        required_fields = self.get_required_fields()
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            raise ValueError(MessageTemplates.get_message("REQUIRED_FIELDS_MISSING", missing_fields = ', '.join(missing_fields)))
        return True

    def validate_update(self, data):
        required_fields = self.get_required_fields_for_ud()
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            raise ValueError(MessageTemplates.get_message("REQUIRED_FIELDS_MISSING", missing_fields = ', '.join(missing_fields)))
        return True

class CategoryMapper:
    def __init__(self):
        self.repository = Repository(connection)
        self.field_mapping = {'pid': 'id',
                                'id': 'category_id',
                                'image': 'image',
                                'long name': 'long_name',
                                'short name': 'short_name',
                                'description': 'description',
                                'active': 'is_active',
                                'created_at': 'created_at',
                                'changed_at': 'changed_at',
                                'changed_by_id': 'changed_by_id',
                                'created_by_id': 'created_by_id',
                                'table': 'db_table' }
        self.get_fields = ['category_id', 'long_name', 'short_name', 'description']
        
    def get_field_mapping(self):
        query = f"SELECT field_name, db_field_name FROM products_fieldconfig WHERE entity_name = 'category'"
        mappings = self.repository.fetch(query)
        return {item['field_name']: item['db_field_name'] for item in mappings}
    
    def get_required_fields(self):
        required_fields = [
            'category_id', 'image', 'long_name', 'short_name', 'description', 'is_active','db_table'
        ]
        return required_fields 
    
    def validate_params(self, params):
        return '' 
        
        
    def get_allowed_fields(self):
        if RequestStore.get_access_level() == 'VIEW' or RequestStore.get_access_level() is None:
            return ", ".join(self.get_fields)
        else:
            return '*'
        
    def get_required_fields_for_ud(self):
        required_fields = [
            'category_id'
        ]
        return required_fields
    def convert_to_db(self,data):
        converted_data = {}
        for param, value in data.items():
            if param in self.field_mapping:
                db_field = self.field_mapping[param]
                converted_data[db_field] = value
            else:
                logger.warning(f'Unexpected parameter: {param}')
        return converted_data
    
    def validate_insert(self, data):
        required_fields = self.get_required_fields()
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            raise ValueError(MessageTemplates.get_message("REQUIRED_FIELDS_MISSING", missing_fields = ', '.join(missing_fields)))
        return True

    def validate_update(self, data):
        required_fields = self.get_required_fields_for_ud()
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            raise ValueError(MessageTemplates.get_message("REQUIRED_FIELDS_MISSING", missing_fields = ', '.join(missing_fields)))
        return True
    
