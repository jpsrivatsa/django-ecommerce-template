import logging
from django.http import JsonResponse

# Set up logger for error logging
logger = logging.getLogger(__name__)

class ParameterValidator:
    def __init__(self, params):
        self.params = params
        self.errors = []

    def validate(self):
        """Validates query parameters."""
        
        # Validate each parameter
        for param, value in self.params.items():
            self._validate_param(param, value)

        # Return errors if there are any
        if self.errors:
            logger.error("Validation errors: %s", self.errors)
            return {"errors": self.errors}

        return self.params 
    
    def _validate_payload(self, param, value):
        expected_type = self._get_expected_type(param)
        if value is None:
            return
        try:
            if not isinstance(value, expected_type):
                # Try to convert to the expected type
                if expected_type == int:
                    value = int(value)  # Convert to integer
                elif expected_type == str:
                    value = str(value)  # Convert to string
            logger.info(f"Parameter {param} validated with value: {value}")
        except ValueError:
            self.errors.append(f"Invalid type for parameter: '{param}'. Expected {expected_type.__name__}, got {type(value).__name__}.")
        except Exception as e:
            self.errors.append(f"Unexpected error validating '{param}': {str(e)}")
            
    def _validate_param(self, param, value):
        expected_type = self._get_expected_type(param)
        if value is None:
            return
        try:
            if not isinstance(value, expected_type):
                # Try to convert to the expected type
                if expected_type == int:
                    value = int(value)  # Convert to integer
                elif expected_type == str:
                    value = str(value)  # Convert to string
            logger.info(f"Parameter {param} validated with value: {value}")
        except ValueError:
            self.errors.append(f"Invalid type for parameter: '{param}'. Expected {expected_type.__name__}, got {type(value).__name__}.")
        except Exception as e:
            self.errors.append(f"Unexpected error validating '{param}': {str(e)}")

    def _get_expected_type(self, param):
        """Maps each parameter to its expected type."""
        mapping = {
            'category_id': str,
            'name': str,
            'status': int,
            'created_by': str,
            'page_size': int,
            'page': int,
            'image': str,
            'long name':str,
            'short name': str,
            'description': str,
            'is_active': int,
            'db_table': str
        }
        return mapping.get(param, str)  # Default to string if not specified
