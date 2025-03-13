from django.shortcuts import render
from shop.models import Product

def product_list(request):
    products = Product.objects.all()
    
    return render(request, 'shop/product_list.html', {'products': products})