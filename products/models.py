from django.db import models
from django.contrib.auth.models import User 
from django.conf import settings
class Category(models.Model):
    category_id = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    long_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100)
    db_table = models.CharField(max_length=100,default="")
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, to_field= 'username',
        related_name='categories_created',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, to_field= 'username',
        related_name='categories_changed',
        on_delete=models.SET_NULL,
        null=True
    )
    changed_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.long_name

class Brand(models.Model):
    brand_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='brand_logos/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, to_field='username',
        related_name='brands_created',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='brands_changed',
        on_delete=models.SET_NULL,
        null=True
    )
    changed_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.name
    
    
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=50, unique=True,null=False, editable=False)
    name = models.CharField(max_length=255,null=False)
    category = models.ForeignKey(Category, to_field='category_id', related_name='product_category', on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brand, to_field='brand_id', related_name='product_brand', on_delete=models.SET_NULL, null=True)
    vendor = models.CharField(max_length=100,null=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='product_created_by', on_delete=models.SET_NULL, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)  # When the product entry was created
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='product_changed_by', on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class FieldConfig(models.Model):
    entity_name = models.CharField(max_length=100) 
    field_name = models.CharField(max_length=100)
    db_field_name = models.CharField(max_length=100)
    is_required = models.BooleanField(default=False)
    access_level = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('entity_name', 'field_name')
    def __str__(self):
        return f"{self.entity_name}: {self.field_name}"
    
class Motherboard(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id', editable=False)
    description = models.TextField()
    category = models.CharField(max_length=255)
    chipset = models.CharField(max_length=255)
    socket = models.CharField(max_length=255)
    form_factor = models.CharField(max_length=255)
    memory_type = models.CharField(max_length=255)
    max_capacity = models.CharField(max_length=255)
    slots = models.CharField(max_length=255)
    supported_speeds = models.CharField(max_length=255)
    m2_slots = models.IntegerField()
    sata_ports = models.IntegerField()
    pcie_slots = models.CharField(max_length=255)
    wired_lan = models.CharField(max_length=255)
    wireless = models.CharField(max_length=255)
    audio_codec = models.CharField(max_length=255)
    channels = models.CharField(max_length=255)
    usb_3_2_gen_2x2_type_c_ports = models.IntegerField()
    usb_3_2_gen_2_type_a_ports = models.IntegerField()
    usb_3_2_gen_1_type_a_ports = models.IntegerField()
    usb_2_0_ports = models.IntegerField()
    lan = models.CharField(max_length=255)
    audio_jack = models.CharField(max_length=255)
    clear_cmos_button = models.CharField(max_length=255)
    usb_3_2_gen_1_headers = models.IntegerField()
    usb_3_2_gen_2_header = models.IntegerField()
    sata_headers = models.IntegerField()
    m2_pcie_headers = models.IntegerField()
    features = models.TextField()
    compatibility = models.CharField(max_length=255)
    warranty = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='motherboards_created', on_delete=models.SET_NULL, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='motherboards_changed', on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.product_id.product_id} - {self.category}'
