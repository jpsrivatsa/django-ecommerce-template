from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartView
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('', csrf_exempt(CartView.as_view()), name='category-view'),
]
