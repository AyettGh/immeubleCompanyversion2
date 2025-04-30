import os.path



from django.contrib.auth.models import AbstractUser
from django.db import models

def product_image_path(instance, filename):
    if instance.id:
        return f'products/{instance.id}/{filename}'
    return f'products/temp/{filename}'

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    role_choices = [
        ('ADMIN', 'Admin'),
        ('CUSTOMER', 'Customer'),
    ]
    role = models.CharField(max_length=200, choices=role_choices, default='CUSTOMER')
    email = models.EmailField(unique=True)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Category(models.Model):
    name=models.CharField(max_length=100)
    created_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='categories_created')
    updated_at=models.DateTimeField(auto_now=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name=models.CharField(max_length=200)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    description=models.TextField()
    image=models.ImageField(upload_to=product_image_path,null=True,blank=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    created_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='products_created')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def delete(self, *args,**kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args,**kwargs)

class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='whishlist_items')
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    added_on=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together=('user','product')
        ordering= ['-added_on']

    def __str__(self):
        return f"{self.user.email}'s wishlist: {self.product.name}"




