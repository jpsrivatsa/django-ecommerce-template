from .models import Cart
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.db import transaction,DatabaseError
from rest_framework.permissions import IsAuthenticated
from django.views import View
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import HasAccessPermission
from django.db import connection
from rest_framework.views import APIView
from .serializers import get_authenticated_user
import json
import logging
from .mappers import CartMapper as mc
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
class CartView(APIView):
    authentication_classes = [JWTAuthentication,IsAuthenticated]
    permission_classes = [HasAccessPermission]
    def get(self, request, *args, **kwargs):
        if request.body:
            return self.get_cart(request)
        else:
            return self.get_cart(request)
    def post(self, request, *args, **kwargs):
        return self.add_to_cart(request)
    def put(self, request, *args, **kwargs):
            return self.update_cart(request)
    def delete(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        if product_id:
            return self.delete_product(product_id)
        return HttpResponseNotAllowed(['DELETE'])
    def get_cart(self, request):
        auth_user = get_authenticated_user(request) # If needed for logging or other purposes
        params = {
            'cart_id': request.GET.get('cart_id')
        }
        query = f"SELECT p.product_name, ca.* FROM cart_cart ca JOIN products_product p ON ca.product_id = p.product_id WHERE ca.user_id = %s"
        query_params = [auth_user]
        # Build the query dynamically based on provided parameters
        for key, value in params.items():
            if value:
                    query += f" AND {key} = %s"
                    query_params.append(value)

        try:
            with connection.cursor() as cursor:
                cart = []
                cursor.execute(query, query_params)
                rows = cursor.fetchall()
                if not rows:
                    return JsonResponse({'error': 'No cart items found for the matching criteria'}, status=404)

                # Convert rows to list of dictionaries
                columns = [col[0] for col in cursor.description]
                categories = [dict(zip(columns, row)) for row in rows]
                
                return JsonResponse(categories, status=200, safe=False)
        
        except DatabaseError as e:
            return JsonResponse({'error': 'Database error, please try again later'}, status=500)

        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
 
    def add_to_cart(self, request):
        auth_user = get_authenticated_user(request)
        with transaction.atomic():
            try:
                mapper = mc()
                response_array = []
                cart_data = json.loads(request.body)
                if len(cart_data) == 0:
                    return JsonResponse({
                            'error': f'Required at least one product in the JSON payload (see documentaion). All transactions rolled back.'
                        }, status=400)
                for data in cart_data:
                    db_data = mapper.convert_to_db(data)
                    db_data['user_id'] = auth_user
                    required_fields = mapper.get_required_fields()
                    missing_fields = [field for field in required_fields if field not in db_data]
                    if missing_fields:
                        transaction.set_rollback(True)
                        return JsonResponse({
                            'error': f'Missing required fields at index {data}: {", ".join(missing_fields)}. All transactions rolled back'
                        }, status=400)
                    columns = ', '.join(db_data.keys())
                    placeholders = ', '.join(['%s'] * len(db_data))
                    values = list(db_data.values())
                    response, status_code = self.insert(columns, placeholders, values,db_data['product_id'],auth_user)
                    response_array.append({
                        'response' : response,
                        'code': status_code
                    })
                return JsonResponse(response_array,status=200,safe=False)

            except json.JSONDecodeError:
                transaction.set_rollback(True)
                return JsonResponse({'error': 'Invalid JSON format. All transactions rolled back'}, status=400)
            

            '''except Exception as e:
                print(e)
                transaction.set_rollback(True)
                return JsonResponse({'error': 'An unexpected error occurred. All transactions rolled back'}, status=500)'''
    
    def insert(self, columns, placeholders, values,id,user):
        check_query = f"SELECT COUNT(*) FROM cart_cart WHERE product_id = %s AND user_id = %s"
        try:
            with connection.cursor() as cursor:
                cursor.execute(check_query,[id,user])
                if cursor.fetchone()[0]>0:
                    print(cursor.fetchone())
                    return {'error': f'Product already exists in cart: {id}'}, 400
            insert_query = f"INSERT INTO cart_cart ({columns}, created_at, changed_at) VALUES ({placeholders}, NOW(),NOW())"
            with connection.cursor() as cursor:
                cursor.execute(insert_query, values)
                return {'message': 'cart Successfully inserted'}, 201

        except DatabaseError as e:
            return {'error': 'Database error, please try again later'}, 500 
    def update_cart(self, request):
        auth_user = get_authenticated_user(request)
        with transaction.atomic():
            try:
                mapper = mc()
                response_array = []
                cart_data = json.loads(request.body)
                for data in cart_data:
                    db_data = mapper.convert_to_db(data)
                    db_data['changed_by_id'] = auth_user  # Track the user who is making the changes
                    required_fields = mapper.get_required_fields_for_ud()
                    missing_fields = [field for field in required_fields if field not in db_data]
                    
                    if missing_fields:
                        transaction.set_rollback(True)
                        return JsonResponse({
                            'error': f'Missing required fields at index {data}: {", ".join(missing_fields)}. All transactions rolled back'
                        }, status=400)

                    columns = ', '.join([f"{key} = %s" for key in db_data.keys()])
                    values = list(db_data.values())
                    response, status_code = self.update(columns, values, db_data['cart_id'])
                    response_array.append({
                        'response': response,
                        'code': status_code
                    })
                
                return JsonResponse(response_array, status=200, safe=False)

            except json.JSONDecodeError:
                transaction.set_rollback(True)
                return JsonResponse({'error': 'Invalid JSON format. All transactions rolled back'}, status=400)

        ''' except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'error': 'An unexpected error occurred. All transactions rolled back'}, status=500)'''

    def update(self, columns, values, id,user):
        check_query = f"SELECT COUNT(*) FROM cart_cart WHERE product_id = %s AND user_id = %s"
        update_query = f"UPDATE products_cart SET {columns}, changed_at = NOW() WHERE product_id = %s AND user_id = %s"
        try:
            with connection.cursor() as cursor:
                cursor.execute(check_query, [id,user])
                if cursor.fetchone()[0] == 0:
                    return {'error': f'Product does not exist in cart.: {id}. Add using post request'}, 400

                # Append the cart_id at the end of values list for the WHERE clause
                values.append(id)
                values.append(user)
                cursor.execute(update_query, values)
                return {'message': f'cart successfully updated. "{id}"'}, 200

        except DatabaseError as e:
            return {'error': 'Database error, please try again later'}, 500

