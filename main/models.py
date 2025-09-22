import uuid
from django.db import models

from django.contrib.auth.models import User

    
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('shoes', 'Shoes'),
        ('apparel', 'Apparel'),
        ('accessories', 'Accessories'),
        ('training', 'Training'),
        ('equipment', 'Equipment'),
        ('ball', 'Ball'),
        ('fans', 'Fans Merchandise'),
    ] 
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    thumbnail = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    product_stock = models.PositiveIntegerField(default=0)
    product_views = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.name
    

    @property
    def is_product_hot(self):
        return self.product_views > 50

    def increment_views(self):
        self.product_views += 1
        self.save()

    def add_stock(self, amount):
        """Menambahkan stok produk"""
        if amount > 0:
            self.product_stock += amount
            self.save()

    def reduce_stock(self, amount):
        """Mengurangi stok produk"""
        if amount > 0 and self.product_stock >= amount:
            self.product_stock -= amount
            self.save()
            return True
        return False
    