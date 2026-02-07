
from rest_framework import viewsets
from .models import Orders
from .serializers import OrdersSerializer

class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
