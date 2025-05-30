from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from shop.views import search_view, iuexam_view
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('shop.urls')),
    path('search/', search_view, name='search'),
    path('iuexam/', iuexam_view, name='iuexam'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)