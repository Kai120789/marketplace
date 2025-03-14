from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import login_view, register, logout_view

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('brands/', views.brand_list, name='brand_list'),
    path('products/<slug:slug>-1/', views.product_detail, name='product_detail'),
    path('products/<slug:slug>/', views.product_variant_detail, name='product_variant_detail'),
    path('categories/<slug:slug>/', views.category_products, name='category_detail'),
    
    path("login/", login_view, name="login"),
    path("register/", register, name="register"),
    path("/logout", logout_view, name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]