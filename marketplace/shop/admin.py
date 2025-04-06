from django.contrib import admin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import (
    UserProfile, Address, Category, Brand, Product, Color, ProductVariant, 
    ProductColor, Review, Basket, Order, BasketOrder, ProductOrder
)

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import fonts
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def generate_pdf(modeladmin, request, queryset):
    # Регистрируем шрифт с поддержкой кириллицы
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    except:
        # Если шрифт не найден, используем стандартный (может не поддерживать кириллицу)
        pdfmetrics.registerFont(TTFont('Arial', 'arialbd.ttf'))
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Устанавливаем шрифт для стилей
    styles['Normal'].fontName = 'Arial'
    styles['Heading1'].fontName = 'Arial'
    
    elements = []
    
    # Заголовок
    elements.append(Paragraph(f"Отчет по модели: {modeladmin.model._meta.verbose_name}", styles['Heading1']))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))
    
    # Содержимое
    for obj in queryset:
        # Создаем строку с основными полями
        fields = []
        for field in obj._meta.fields:
            if field.name not in ['created_at', 'updated_at']:  # Пропускаем служебные поля
                field_value = str(getattr(obj, field.name))
                fields.append(f"{field.verbose_name}: {field_value}")
        
        obj_str = "<br/>".join(fields)
        elements.append(Paragraph(obj_str, styles['Normal']))
        elements.append(Paragraph("<br/>----------------------<br/>", styles['Normal']))
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

generate_pdf.short_description = "Сгенерировать PDF отчет"

class ExportToPDFMixin:
    actions = [generate_pdf]

@admin.register(UserProfile)
class UserProfileAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("user", "phone", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "phone")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('user', 'phone', 'role', 'avatar', 'resume', 'website', 'created_at', 'updated_at')
        }),
    )
    autocomplete_fields = ("user",)

@admin.register(Address)
class AddressAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("user", "country", "city", "street", "index", "created_at")
    list_filter = ("country", "city")
    search_fields = ("street", "city", "index")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('user', 'country', 'city', 'street', 'index', 'map_link', 'created_at', 'updated_at')
        }),
    )
    autocomplete_fields = ("user",)

@admin.register(Category)
class CategoryAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'photo', 'documentation', 'created_at', 'updated_at')
        }),
    )

@admin.register(Brand)
class BrandAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('name', 'photo', 'description', 'official_website', 'catalog_pdf', 'created_at', 'updated_at')
        }),
    )

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('name', 'color', 'price', 'photo', 'technical_drawing', 'product_url')

@admin.register(Product)
class ProductAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("name", "category", "brand", "default_price", "created_at")
    list_filter = ("category", "brand")
    search_fields = ("name", "slug")
    inlines = [ProductVariantInline]
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'photo', 'category', 'brand', 'default_price', 
                      'avg_rating', 'description', 'manual', 'video_url', 
                      'created_at', 'updated_at')
        }),
    )
    autocomplete_fields = ("category", "brand")

@admin.register(Color)
class ColorAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("name", "color", "created_at")
    search_fields = ("name", "color")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('name', 'color', 'image', 'palette_file', 'created_at', 'updated_at')
        }),
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("name", "product", "color", "price", "created_at")
    list_filter = ("color", )
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'product', 'color', 'photo', 'category',
                      'description', 'images', 'brand', 'price', 'technical_drawing',
                      'product_url', 'created_at', 'updated_at')
        }),
    )
    autocomplete_fields = ("product", "color", "category", "brand")

@admin.register(ProductColor)
class ProductColorAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("product", "color")
    list_filter = ("color", )
    autocomplete_fields = ("product", "color")

@admin.register(Review)
class ReviewAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("product", "rating", "name", "created_at")
    list_filter = ("created_at", )
    search_fields = ("name", "description")
    fieldsets = (
        (None, {
            'fields': ('product', 'rating', 'name', 'description', 'photo', 'video_review_url', 'created_at', 'updated_at')
        }),
    )
    autocomplete_fields = ("product",)

class BasketOrderInline(admin.TabularInline):
    model = BasketOrder
    extra = 1

@admin.register(Basket)
class BasketAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("user", "product", "product_variant", "count", "created_at")
    list_filter = ("user",)
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('user', 'product', 'product_variant', 'count', 'created_at', 'updated_at')
        }),
    )
    autocomplete_fields = ("user", "product", "product_variant")

@admin.register(Order)
class OrderAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("user", "full_price", "created_at")
    list_filter = ("user", "created_at")
    search_fields = ("user__username",)
    inlines = [BasketOrderInline]
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('user', 'address', 'full_price', 'invoice', 'tracking_url', 'created_at', 'updated_at')
        }),
    )
    autocomplete_fields = ("user", "address")

@admin.register(BasketOrder)
class BasketOrderAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("basket", "order", "count")
    autocomplete_fields = ("basket", "order")

@admin.register(ProductOrder)
class ProductOrderAdmin(ExportToPDFMixin, admin.ModelAdmin):
    list_display = ("product", "product_variant", "order")
    list_filter = ("order", )
    autocomplete_fields = ("product", "product_variant", "order")