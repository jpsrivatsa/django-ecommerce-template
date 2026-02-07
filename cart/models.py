
from django.db import models
from django.conf import settings
from products.models import Product
class Cart(models.Model):
    product = models.ForeignKey(Product,to_field='product_id',related_name='product', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveBigIntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='username',
        related_name='cart_owner',
        on_delete=models.SET_NULL,
        null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    class Meta:
        unique_together = ('user', 'product')
    
    
    
