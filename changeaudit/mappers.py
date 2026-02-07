from django.apps import apps
from django.core.exceptions import ValidationError
import logging
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

class CategoryMapper:
    def __init__(self):
        self.field_mapping = {
            'id': 'category_id',
            'image': 'image',
            'long name': 'long_name',
            'short name': 'short_name',
            'description': 'description',
            'active':'is_active',
            'table':'db_table'
        }
    def get_required_fields(self):
        required_fields = [
            'category_id', 'image', 'long_name', 'short_name', 'description', 'is_active','db_table'
        ]
        return required_fields 
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
    
