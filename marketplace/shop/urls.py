from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import add_to_cart, cart_view, login_view, register, logout_view, remove_from_cart, brand_detail

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/<int:brand_id>/', brand_detail, name='brand_detail'),
    path('products/<slug:slug>-1/', views.product_detail, name='product_detail'),
    path('products/<slug:slug>/', views.product_variant_detail, name='product_variant_detail'),
    path('categories/<slug:slug>/', views.category_products, name='category_detail'),
    
    path("login/", login_view, name="login"),
    path("register/", register, name="register"),
    path("logout/", logout_view, name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    path("add-to-cart/<int:variant_id>/", add_to_cart, name="add_to_cart"),
    path("cart/", cart_view, name="cart_view"),
    path("remove-from-cart/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
]