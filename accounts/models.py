from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField
from django.conf import settings
class AccessLevel(models.TextChoices):
    EDIT = 'edit', 'Edit'
    VIEW = 'view', 'View'
    CREATE = 'create', 'Create'

class Roles(models.Model):
    role = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    product_access = models.CharField(
        max_length=10,
        choices=AccessLevel.choices,
        default=AccessLevel.VIEW
    )
    account_access = models.CharField(
        max_length=10,
        choices=AccessLevel.choices,
        default=AccessLevel.VIEW
    )
    payment_access = models.CharField(
        max_length=10,
        choices=AccessLevel.choices,
        default=AccessLevel.VIEW
    )
    order_access = models.CharField(
        max_length=10,
        choices=AccessLevel.choices,
        default=AccessLevel.VIEW
    )
    cart_access = models.CharField(
        max_length=10,
        choices=AccessLevel.choices,
        default=AccessLevel.VIEW
    )
    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['-created_at']
        
class UserManager(BaseUserManager):
    def create_user(self, username, phone_number, email, password=None, **extra_fields):
        if not username:
            raise ValueError(('The Username field must be set'))
        user = self.model(username=username, phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, phone_number, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(username=username)

class User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = EncryptedCharField(max_length=100, blank=False, null=False)  # Password will be stored as a hash
    role = models.ForeignKey(Roles, to_field='role', related_name='user_role', on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number','email']
    is_active = models.BooleanField(default=True)
    objects = UserManager()
    def __str__(self):
        return self.username
    
    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def save(self, *args, **kwargs):
        if not self.pk:  # Only hash the password if it's a new user
            self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

class Address(models.Model):
    address_id = models.AutoField(primary_key=True, unique=True)  # Unique address identifier
    user = models.ForeignKey(User, to_field='username', on_delete=models.CASCADE, related_name='addresses')
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.address_line_1}, {self.city}, {self.country}'

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ['-created_at']
    
class PaymentMethod(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('UPI', 'UPI'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]
    payment_method_id = models.AutoField(primary_key=True, unique=True)  # Unique payment method identifier
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')  # Link to User
    method_type = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)  # Type of payment method
    card_number = EncryptedCharField(max_length=20, blank=True, null=True)
    card_expiry_date = EncryptedCharField(max_length=5, blank=True, null=True)
    card_cvc = EncryptedCharField(max_length=4, blank=True, null=True)
    paypal_email = EncryptedCharField(max_length=254, blank=True, null=True)
    bank_account_number = EncryptedCharField(max_length=30, blank=True, null=True)
    bank_name = EncryptedCharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.get_method_type_display()} - {self.user.username}'

    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['-created_at']
        

