from django.shortcuts import render
from django.core.paginator import Paginator
from shop.models import Product, Brand

def product_list(request):
    products_list = Product.objects.all()

    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    return render(request, 'shop/product_list.html', {'products': products})

def brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'shop/brand_list.html', {'brands': brands})

def index(request):
    products = Product.objects.all()[:4]
    brands = Brand.objects.all()[:6]
    
    return render(request, 'shop/index.html', {
        'products': products,
        'brands': brands,
    })