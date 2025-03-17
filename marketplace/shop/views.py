from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from shop.models import Category, Product, Brand, ProductVariant
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views import View
from .models import Basket, Product, Category, Brand
from django.db.models import Q
from django.contrib import messages
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST




def product_list(request):
    category_id = request.GET.get("category")
    brand_id = request.GET.get("brand")
    sort_by = request.GET.get("sort", "default_price")  # Сортировка по умолчанию — по цене

    products_list = Product.objects.all()
    

    if category_id:
        products_list = products_list.filter(category_id=category_id)

    if brand_id:
        products_list = products_list.filter(brand_id=brand_id)

    if sort_by in ["default_price", "-default_price", "created_at", "-created_at"]:
        products_list = products_list.order_by(sort_by)
        
    paginator = Paginator(products_list, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

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
    


def get_tokens_for_user(user):
    """Генерация access и refresh токенов"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Пользователь с таким именем уже существует.")
            return render(request, "auth/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Пользователь с таким email уже существует.")
            return render(request, "auth/register.html")

        user = User.objects.create_user(username=username, email=email, password=password)
        tokens = get_tokens_for_user(user)

        messages.success(request, "Регистрация успешна! Можете войти.")
        response = redirect("/shop/")
        response.set_cookie("access_token", tokens["access"], httponly=True)
        response.set_cookie("refresh_token", tokens["refresh"], httponly=True)
        return response

    return render(request, "auth/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            tokens = get_tokens_for_user(user)

            response = redirect("/shop/")
            response.set_cookie("access_token", tokens["access"], httponly=True, max_age=900)  # 15 минут
            response.set_cookie("refresh_token", tokens["refresh"], httponly=True, max_age=604800)  # 7 дней
            return response
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
            return render(request, "auth/login.html")

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    response = redirect("login")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response




@csrf_exempt
@require_POST
@login_required
def add_to_cart(request, variant_id):
    product_variant = get_object_or_404(ProductVariant, id=variant_id)
    Basket.add_to_cart(request.user, product_variant)
    return JsonResponse({"success": True, "message": "Товар добавлен в корзину"})

@login_required
def cart_view(request):
    basket_items = Basket.objects.filter(user=request.user)
    total_price = sum(item.product_variant.price * item.count for item in basket_items)
    return render(request, "cart.html", {"basket_items": basket_items, "total_price": total_price})

@login_required
def remove_from_cart(request, item_id):
    basket_item = get_object_or_404(Basket, id=item_id, user=request.user)
    basket_item.delete()
    return redirect("cart_view")


def brand_detail(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    return render(request, 'shop/brand_detail.html', {'brand': brand})