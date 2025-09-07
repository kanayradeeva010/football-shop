import uuid
from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('shoes', 'Shoes'),
        ('apparel', 'Apparel'),
        ('accessories', 'Accessories'),
        ('training', 'Training'),
        ('equipment', 'Equipment'),
        ('ball', 'Ball'),
        ('fans', 'Fans Merchandise')
    ] 
    
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    thumbnail = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    thumbnail = models.URLField(blank=True, null=True)
    product_likes = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    

    def increment_views(self):
        self.product_likes += 1
        self.save()