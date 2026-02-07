from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed

def get_authenticated_user(request):
    if not request.user.is_authenticated:
        raise AuthenticationFailed('Invalid Authentication token')
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        raise AuthenticationFailed('Authorization header is missing or invalid.')
    
    token_text = auth[len('Bearer '):]
    try:
        token = AccessToken(token_text)
        return token.get('username', None)
    except Exception as e:
        raise AuthenticationFailed(f'Error decoding token: {str(e)}')
