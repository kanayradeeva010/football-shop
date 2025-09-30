from .models import Product

def product_categories(request):
    return {
        'PRODUCT_CATEGORIES': Product.CATEGORY_CHOICES 
    }