from django.apps import apps
from django.core.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)
class CartMapper:
    def __init__(self):
        self.field_mapping = {
            'product': 'product_id',
            'quantity':'quantity'
        }
    def get_required_fields(self):
        required_fields = [
            'product_id','quantity'
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
    
