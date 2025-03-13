from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('products/', views.product_list, name='product_list'),  # Список товаров
    path('brands/', views.brand_list, name='brand_list'),  # Список товаров
]