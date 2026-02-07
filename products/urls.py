from django.urls import path
from .views import ProductView
from .views import CategoryView
from .views import BrandView
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('product', ProductView.as_view(), name='product-view'),
    path('categories', CategoryView.as_view(), name='category-view'),
    path('brands',BrandView.as_view(), name='brands-view')
]
