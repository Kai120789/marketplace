from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import add_to_cart, cart_view, login_view, register, logout_view, remove_from_cart, brand_detail, product_create, product_update, product_delete, review_create, review_delete, product_variant_create, product_variant_update, product_variant_delete
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.urls import path, include

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

    path('products/create/', product_create, name='product_create'),
    path('products/<int:pk>/update/', product_update, name='product_update'),
    path('products/<int:pk>/delete/', product_delete, name='product_delete'),
    path('reviews/create/<int:product_id>/', review_create, name='review_create'),
    path('reviews/<int:pk>/delete/', review_delete, name='review_delete'),

    path('product/<slug:product_slug>/variant/create/', views.product_variant_create, name='product_variant_create'),
    path('variant/<slug:slug>/edit/', views.product_variant_update, name='product_variant_update'),
    path('variant/<slug:slug>/delete/', views.product_variant_delete, name='product_variant_delete'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns