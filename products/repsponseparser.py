import time
from .messages import MessageTemplates
class ResponseParser:
    @staticmethod
    def parse_response(request, data, entity):
        query_params = request.query_params.dict()
        path_vars = request.parser_context.get('kwargs', {})
        headers = {key: value for key, value in request.headers.items() if key.lower() != 'authorization'}
        response = {
            'method': request.method,
            'path': request.path,
            'query_params': query_params,
            'path_variables': path_vars,
            'headers': headers,
            'metadata': {
                'Count': len(data),
                'Timestamp': str(time.time()),
                'Page': query_params.get('page', None),
                'Page Size': query_params.get('page_size', None),
            }
        }
        if request.data:
            response['payload'] = request.data
        if not data:
            response['error'] = MessageTemplates.get_message("NOT_FOUND",entity_name=entity)
        if 'errors' in data:
            response['error'] = data['errors']
        else:
            response['results'] = data
        return response
