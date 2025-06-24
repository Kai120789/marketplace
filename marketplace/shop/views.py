from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.contrib import messages
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import (
    Category, Product, Brand, ProductVariant, Review, Basket,
    Order, BasketOrder, ProductOrder, UserProfile, Address
)
from .forms import ProductForm, ReviewForm, OrderForm, ProductVariantForm
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    ProductSerializer, CategorySerializer, BrandSerializer,
    ProductVariantSerializer, ReviewSerializer
)
from simple_history.models import HistoricalRecords
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from django_filters import FilterSet, CharFilter, NumberFilter
from rest_framework.pagination import PageNumberPagination


# Дополнительные фильтры для Product
class ProductFilter(FilterSet):
    min_price = NumberFilter(field_name='default_price', lookup_expr='gte')
    max_price = NumberFilter(field_name='default_price', lookup_expr='lte')
    category = CharFilter(field_name='category__slug')
    brand = CharFilter(field_name='brand__slug')
    
    class Meta:
        model = Product
        fields = ['category', 'brand', 'min_price', 'max_price']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'default_price']
    search_fields = ['name', 'description']
    ordering_fields = ['default_price', 'created_at', 'avg_rating']
    pagination_class = PageNumberPagination
    filter_class = ProductFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        
        user = self.request.user
        if user.is_authenticated:
            favorites = self.request.query_params.get('favorites', None)
            if favorites:
                queryset = queryset.filter(favorited_by=user.profile)
        
        return queryset

    @action(detail=False, methods=['get'])
    def discounted(self, request):
        products = Product.objects.filter(
            Q(default_price__lt=1000) & 
            ~Q(category__name='Премиум') |
            Q(brand__name__icontains='sale')
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_to_favorites(self, request, pk=None):
        product = self.get_object()
        request.user.profile.favorites.add(product)
        return Response({'status': 'added to favorites'})

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        # Еще один комплексный запрос с Q, AND и OR
        products = Product.objects.filter(
            Q(avg_rating__gte=4) & 
            (Q(review_count__gte=10) | Q(featured=True))
        ).order_by('-avg_rating')[:10]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'color', 'price']

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'rating']

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        if Review.objects.filter(product=product, user=self.request.user).exists():
            raise serializer.ValidationError("Вы уже оставляли отзыв на этот товар")
        
        if not Order.objects.filter(
            user=self.request.user,
            products__product=product
        ).exists():
            raise serializer.ValidationError("Вы не можете оставить отзыв, не купив товар")
        
        serializer.save(user=self.request.user)

# Standard Views
def product_list(request):
    products_list = Product.objects.all()
    
    # Фильтрация
    category_id = request.GET.get("category")
    brand_id = request.GET.get("brand")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    
    if category_id:
        products_list = products_list.filter(category_id=category_id)
    if brand_id:
        products_list = products_list.filter(brand_id=brand_id)
    if min_price:
        products_list = products_list.filter(default_price__gte=min_price)
    if max_price:
        products_list = products_list.filter(default_price__lte=max_price)

    search_query = request.GET.get("q")
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        ).distinct()

    if request.user.is_authenticated:
        favorites_only = request.GET.get("favorites")
        if favorites_only:
            products_list = products_list.filter(favorited_by=request.user.profile)
    
    # Сортировка
    sort_by = request.GET.get("sort", "default_price")
    if sort_by in ["default_price", "-default_price", "created_at", "-created_at", "avg_rating", "-avg_rating"]:
        products_list = products_list.order_by(sort_by)
    
    # Пагинация
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

from django.shortcuts import render
from django.db.models import Count, Avg, Q
from .models import Category, Product, Brand, Review

def index(request):
    total_categories = Category.objects.count()
    total_products = Product.objects.count()
    total_brands = Brand.objects.count()
    
    categories = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('-product_count')[:12]
    
    popular_products = Product.objects.filter(
        avg_rating__gt=3
    ).order_by('-avg_rating')[:8]
    
    top_brands = Brand.objects.annotate(
        product_count=Count('product')
    ).filter(
        product_count__gt=0
    ).order_by('-product_count')[:6]
    
    average_rating = Product.objects.aggregate(
        avg_rating=Avg('avg_rating')
    )['avg_rating'] or 0
    
    products_without_reviews = Product.objects.annotate(
        review_count=Count('review')
    ).filter(
        review_count=0
    ).order_by('?')[:4]
    
    featured_categories = Category.objects.distinct()[:3]
    
    try:
        featured_product = Product.objects.get(
            Q(name__icontains='новинка') | Q(name__icontains='хит'),
            avg_rating__gte=4
        )
    except Product.DoesNotExist:
        featured_product = None
    
    return render(request, 'shop/index.html', {
        'total_categories': total_categories,
        'total_products': total_products,
        'total_brands': total_brands,
        'categories': categories,
        'popular_products': popular_products,
        'top_brands': top_brands,
        'average_rating': round(average_rating, 1),
        'products_without_reviews': products_without_reviews,
        'featured_categories': featured_categories,
        'featured_product': featured_product,
    })
 
def product_detail(request, slug):
    product_variant = get_object_or_404(ProductVariant, slug=f"{slug}-{1}")
    all_product_variants = ProductVariant.objects.filter(slug__startswith=f"{slug}-").select_related('color')

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
        response = redirect("/shop/login")
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
            response.set_cookie("access_token", tokens["access"], httponly=True, max_age=1500)  # 15 минут
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
    basket_items = Basket.objects.filter(user=request.user).select_related('product_variant', 'product_variant__product')
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




@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.added_by = request.user
            product.save()  # Теперь сохраняем с дополнительными данными
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'shop/product_form.html', {'form': form})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/product_form.html', {'form': form})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user.profile.role != 'admin':
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно обновлен')
            return redirect('product_detail', slug=product.slug)
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/product_form.html', {'form': form})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user.profile.role != 'admin':
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар успешно удален')
        return redirect('product_list')
    return render(request, 'shop/product_confirm_delete.html', {'object': product})

@login_required
def review_create(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.user.profile.role != 'admin':
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.save()
            return redirect('product_detail', slug=product.slug)
    else:
        form = ReviewForm()
    return render(request, 'shop/review_form.html', {'form': form})

@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user.profile.role != 'admin':
        return HttpResponseForbidden()
    
    review.delete()
    messages.success(request, 'Отзыв успешно удален')
    return redirect('product_detail', slug=review.product.slug)


from django.http import JsonResponse
from django.db.models import Q
from .models import Category, Brand, Product

def search_view(request):
    query = request.GET.get('q', '').strip()
    results = {
        'categories': [],
        'brands': [],
        'products': []
    }

    if query:
        categories = Category.objects.filter(
            Q(name__icontains=query)
        ).values('id', 'name', 'slug', 'photo')[:5]
        results['categories'] = list(categories)

        brands = Brand.objects.filter(
            Q(name__icontains=query)
        ).values('id', 'name', 'photo')[:5]
        results['brands'] = list(brands)

        products = Product.objects.filter(
            Q(name__icontains=query)
        ).values('id', 'name', 'slug', 'photo', 'default_price')[:5]
        # Добавляем '-1' к slug
        product_list = list(products)
        for product in product_list:
            product['slug'] = f"{product['slug']}-1"
        results['products'] = product_list

    return JsonResponse(results)


@login_required
def product_variant_create(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if request.method == 'POST':
        form = ProductVariantForm(request.POST, request.FILES)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.slug = f"{product.slug}-{ProductVariant.objects.filter(product=product).count() + 1}"
            variant.save()
            return redirect('product_variant_detail', slug=variant.slug)
    else:
        form = ProductVariantForm(initial={'product': product})
    return render(request, 'shop/product_variant_form.html', {
        'form': form,
        'product': product
    })

@login_required
def product_variant_update(request, slug):
    variant = get_object_or_404(ProductVariant, slug=slug)
    if request.method == 'POST':
        form = ProductVariantForm(request.POST, request.FILES, instance=variant)
        if form.is_valid():
            form.save()
            return redirect('product_variant_detail', slug=variant.slug)
    else:
        form = ProductVariantForm(instance=variant)
    return render(request, 'shop/product_variant_form.html', {
        'form': form,
        'variant': variant
    })

@login_required
def product_variant_delete(request, slug):
    variant = get_object_or_404(ProductVariant, slug=slug)
    product_slug = variant.product.slug
    if request.method == 'POST':
        variant.delete()
        return redirect('product_detail', slug=product_slug)
    return render(request, 'shop/product_variant_confirm_delete.html', {'variant': variant})