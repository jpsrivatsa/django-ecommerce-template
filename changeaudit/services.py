from .mappers import CategoryMapper as mc
import json
from django.db import transaction
class CategoryService:
    def __init__(self, repository, cache_strategy):
        self.repository = repository
        self.cache_strategy = cache_strategy

    def get_categories(self, params):
        cache_key = f"category_{params['category_id']}_{params['name']}_{params['status']}_{params['created_by']}"
        cached_data = self.cache_strategy.get(cache_key)
        if cached_data:
            return cached_data
        query = f"SELECT * FROM products_category WHERE 1=1"
        query_params = []
        for key, value in params.items():
            if value:
                if key == 'name':
                    query += f" AND long_name LIKE %s OR short_name LIKE %s"
                    query_params.append(f'%{value}%')
                    query_params.append(f'%{value}%')
                else:
                    query += f" AND {key} = %s"
                    query_params.append(value)
        query += " ORDER BY short_name LIMIT 10 OFFSET 10"
        categories = self.repository.fetch(query, query_params)
        #self.cache_strategy.set(cache_key, categories, timeout=60 * 15)
        return categories

    def create_category(self, request):
        responses = []
        data = json.loads(request.body)
        mapper = mc()
        with self.repository.connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        with transaction.atomic():
            for category in data:
                data_db = mapper.convert_to_db(category)
                if self.repository.exists('category', data_db['category_id']):
                    responses.append({'error': f'Category ID already exists: {data_db["category_id"]}'})
                    continue
                columns = ', '.join(data_db.keys())
                values = list(category.values())
                db_response = self.repository.insert('category',columns, values)
                if db_response == True:
                    responses.append({'message': 'Category successfully created'})
                else:
                    return db_response,500
        return responses,201

    def update_category(self, request):
        responses = []
        data = json.loads(request.body)
        mapper = mc()
        with self.repository.connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        with transaction.atomic():
            for category in data:
                data_db = mapper.convert_to_db(category)
                category_id = data_db['category_id']  # Get the category ID for updating
                if not self.repository.exists('category', category_id):
                    responses.append({'error': f'Category ID does not exist: {category_id}'})
                    continue
                columns = ', '.join([f"{col} = %s" for col in data_db.keys()])
                values = list(data_db.values())
                db_response = self.repository.update('category', columns, values, category_id)
                if db_response == True:
                    responses.append({'message': 'Category successfully updated'})
                else:
                    return db_response, 500

        return responses, 200

        