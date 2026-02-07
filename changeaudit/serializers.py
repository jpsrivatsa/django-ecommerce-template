from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed
def get_authenticated_user(request):
    auth = request.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        raise AuthenticationFailed('Authorization header is missing or invalid.')
    token_text = auth[len('Bearer '):]
    try:
        token = AccessToken(token_text)
        return token.get('username', None)
    except Exception as e:
        raise AuthenticationFailed(f'Error decoding token: {str(e)}')

def has_edit_access(request,table):
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        raise AuthenticationFailed('Authorization header is missing or invalid.')
    
    token_text = auth[len('Bearer '):]
    try:
        token = AccessToken(token_text)
        if token.get(f'{table}_access', None) in ['EDIT','CREATE']:
            return True
        else:
            return False
    except Exception as e:
        raise AuthenticationFailed(f'Error decoding token: {str(e)}')

def has_create_access(request,table):
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        raise AuthenticationFailed('Authorization header is missing or invalid.')
    
    token_text = auth[len('Bearer '):]
    try:
        token = AccessToken(token_text)
        if token.get(f'{table}_access', None) in ['CREATE']:
            return True
        else:
            return False
    except Exception as e:
        raise AuthenticationFailed(f'Error decoding token: {str(e)}')