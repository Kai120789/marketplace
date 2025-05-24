from django.contrib import admin
from django.urls import path, include
from shop.views import search_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('shop.urls')),
    path('search/', search_view, name='search'),

]