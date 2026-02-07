from django.http import JsonResponse, HttpResponseNotAllowed
from django.views import View
from django.contrib.auth import authenticate, login
from django.db import connection
from rest_framework_simplejwt.tokens import RefreshToken
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from .models import Roles
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.middleware.csrf import get_token
from accounts.models import User
class userView(View):
    user = User()
    def post(self, request, *args, **kwargs):
        return self.create_user(request)
    
    def get(self, request, *args, **kwargs):
        return self.validate_user(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id:
            return self.update_user(request, user_id)
        return HttpResponseNotAllowed(['PUT'])

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id:
            return self.delete_user(user_id)
        return HttpResponseNotAllowed(['DELETE'])

    def user_exists(self, body):
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT username from accounts_user WHERE username = %s
        """, [body.get('username')])
            if cursor.fetchall():
                cursor.close()
                return "duplicate_username"
            
    def create_user(self, request):
        data = json.loads(request.body)
        if self.user_exists(data) == "duplicate_username":
            return JsonResponse({'message': 'username exist'}, status=400)
        self.user.username = data.get('username')
        self.user.first_name = data.get('first_name')
        self.user.last_name = data.get('last_name')
        self.user.email = data.get('email')
        self.user.password = (data.get('password'))
        self.user.phone_number = data.get('phone_number')
        self.user.save()
        now = timezone.now()
        return JsonResponse({'message': 'user created successfully'}, status=201)

    def update_user(self, request, user_id):
        data = json.loads(request.body)
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        stock = data.get('stock')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE accounts_user
                SET name = %s, description = %s, price = %s, stock = %s
                WHERE id = %s
            """, [name, description, price, stock, user_id])

        return JsonResponse({'message': 'user updated successfully'})

    def delete_user(self, user_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM accounts_user WHERE id = %s", [user_id])

        return JsonResponse({'message': 'user deleted successfully'})
    
class LoginView(View):
    def post(self, request, *args, **kwargs):
        return self.validate_user(request)
    
    def validate_user(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        try:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # Log the user in
                tokens = self.get_tokens_for_user(user)  # Generate tokens
                return JsonResponse({'message': 'Login successful', 'tokens': tokens}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=400)
    
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        
    def get_tokens_for_user(self,user):
        refresh = RefreshToken.for_user(user)
    
    # Fetch the complete Roles object using the role field from the user model
        role = Roles.objects.filter(role=user.role_id).first()  # Adjust the field name if necessary
        if role:
            # Add custom claims to the payload
            refresh.payload['username'] = user.username
            refresh.payload['product_access'] = role.product_access
            refresh.payload['account_access'] = role.account_access
            refresh.payload['payment_access'] = role.payment_access
            refresh.payload['order_access'] = role.order_access
            refresh.payload['cart_access'] = role.cart_access

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        