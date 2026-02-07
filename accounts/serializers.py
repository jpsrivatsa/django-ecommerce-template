from rest_framework import serializers
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'
