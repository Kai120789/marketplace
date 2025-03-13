from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from shop.models import Category, Product, Brand, ProductVariant

from django.shortcuts import render
from .models import Product, Category, Brand
from django.db.models import Q

def product_list(request):
    category_id = request.GET.get("category")
    brand_id = request.GET.get("brand")
    sort_by = request.GET.get("sort", "default_price")  # Сортировка по умолчанию — по цене

    products = Product.objects.all()

    if category_id:
        products = products.filter(category_id=category_id)

    if brand_id:
        products = products.filter(brand_id=brand_id)

    if sort_by in ["default_price", "-default_price", "created_at", "-created_at"]:
        products = products.order_by(sort_by)

    categories = Category.objects.all()
    brands = Brand.objects.all()

    return render(request, "shop/product_list.html", {
        "products": products,
        "categories": categories,
        "brands": brands,
        "selected_category": category_id,
        "selected_brand": brand_id,
        "sort_by": sort_by,
    })


def brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'shop/brand_list.html', {'brands': brands})

def index(request):
    categories = Category.objects.all()
    products = Product.objects.all()[:4]
    brands = Brand.objects.all()[:6]
    
    return render(request, 'shop/index.html', {
        'products': products,
        'brands': brands,
        'categories': categories,
    })
    
def product_detail(request, slug):
    product_variant = get_object_or_404(ProductVariant, slug=f"{slug}-{1}")
    all_product_variants = ProductVariant.objects.filter(slug__startswith=f"{slug}-")

    return render(request, 'shop/product_detail.html', {
        'product_variant': product_variant,
        'all_product_variants': all_product_variants,
    })

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)

    return render(request, 'shop/category_products.html', {
        'category': category,
        'products': products
    })
    
    
def product_variant_detail(request, slug):
    product_variant = get_object_or_404(ProductVariant, slug=slug)
    all_product_variants = ProductVariant.objects.filter(slug__startswith=slug[0:-1])

    return render(request, 'shop/product_detail.html', {
        'product_variant': product_variant,
        'all_product_variants': all_product_variants,
    })