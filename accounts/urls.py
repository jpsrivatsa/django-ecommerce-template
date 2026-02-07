from django.urls import path
from .views import userView
from .views import LoginView
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('user',csrf_exempt(userView.as_view()),name='create_user'),
    path('login',csrf_exempt(LoginView.as_view()),name='login')
]
