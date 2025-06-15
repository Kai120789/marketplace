from django.contrib import admin
from django.http import HttpResponse
from django import forms
from django.db.models import Q
from io import BytesIO
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from .models import (
    UserProfile, Address, Category, Brand, Product, Color, ProductVariant,
    ProductColor, Review, Basket, Order, BasketOrder, ProductOrder
)


# --- PDF Export ---

def generate_pdf(modeladmin, request, queryset):
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    except Exception:
        pdfmetrics.registerFont(TTFont('Arial', 'arialbd.ttf'))

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'Arial'
    styles['Heading1'].fontName = 'Arial'

    elements = []
    elements.append(Paragraph(f"Отчет по модели: {modeladmin.model._meta.verbose_name}", styles['Heading1']))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    for obj in queryset:
        fields = []
        for field in obj._meta.fields:
            if field.name not in ['created_at', 'updated_at']:
                value = str(getattr(obj, field.name))
                fields.append(f"{field.verbose_name}: {value}")
        elements.append(Paragraph("<br/>".join(fields), styles['Normal']))
        elements.append(Paragraph("<br/>----------------------<br/>", styles['Normal']))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


generate_pdf.short_description = "Сгенерировать PDF отчет"


# --- Excel Export Mixin ---

class ExportToExcelMixin:
    actions = ['export_as_excel', generate_pdf]

    def get_export_queryset(self, request, queryset):
        if hasattr(self.model, 'created_at'):
            q = Q(created_at__gte='2023-01-01')
            
            model_fields = [f.name for f in self.model._meta.get_fields()]
            
            if 'user' in model_fields:
                q &= ~Q(user__is_staff=True)
            if 'phone' in model_fields:
                q &= ~Q(phone__exact='')

            queryset = queryset.filter(q)

        return queryset


    def dehydrate_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y %H:%M') if obj.created_at else ''

    def dehydrate_updated_at(self, obj):
        return obj.updated_at.strftime('%d-%m-%Y %H:%M') if obj.updated_at else ''

    def get_export_fields(self):
        """
        Возвращаем список полей, которые хотим экспортировать в Excel.
        """
        fields = []
        for field in self.model._meta.fields:
            if field.name not in ['id']:
                fields.append(field.name)
        return fields

    def get_field_value_for_excel(self, obj, field_name):
        val = getattr(obj, field_name, '')

        if val is None:
            return ''

        if not isinstance(val, (str, int, float, bool)) and hasattr(val, '__str__'):
            return str(val)

        if hasattr(val, 'url'):
            return val.url

        return val


    def export_as_excel(self, request, queryset):
        queryset = self.get_export_queryset(request, queryset)

        wb = Workbook()
        ws = wb.active
        ws.title = f"Отчет {self.model._meta.verbose_name}"

        fields = self.get_export_fields()
        headers = [self.model._meta.get_field(f).verbose_name for f in fields]
        ws.append(headers)

        for obj in queryset:
            row = []
            for field in fields:
                method_name = f'dehydrate_{field}'
                if hasattr(self, method_name):
                    val = getattr(self, method_name)(obj)
                else:
                    val = self.get_field_value_for_excel(obj, field)
                row.append(val)
            ws.append(row)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"{self.model._meta.verbose_name}_export.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response


    export_as_excel.short_description = "Экспортировать выбранные в Excel"


# --- Пример кастомной валидации для UserProfile ---

class UserProfileAdminForm(forms.ModelForm):
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Телефон обязателен для заполнения.")
        if len(phone) < 10:
            raise forms.ValidationError("Телефон должен содержать не менее 10 символов.")
        return phone

    def clean_role(self):
        role = self.cleaned_data.get('role')
        allowed_roles = ['consumer', 'admin']
        if role not in allowed_roles:
            raise forms.ValidationError(f"Роль должна быть одной из {allowed_roles}")
        return role

    def clean(self):
        cleaned_data = super().clean()
        website = cleaned_data.get('website')
        resume = cleaned_data.get('resume')
        if not website and not resume:
            raise forms.ValidationError("Должен быть заполнен хотя бы сайт или резюме.")
        return cleaned_data


# --- Пример admin actions с GET и POST ---

def mark_as_moderator(modeladmin, request, queryset):
    updated = queryset.update(role='moderator')
    modeladmin.message_user(request, f"Отмечено как модераторы: {updated} профилей.")

mark_as_moderator.short_description = "Пометить выбранные профили как модераторов"


@admin.action(description="Отметить все товары с ценой выше 10000")
def mark_expensive_products(modeladmin, request, queryset):
    count = queryset.filter(price__gt=10000).update(description="Высокая цена")
    modeladmin.message_user(request, f"Обновлено описаний у {count} товаров")


# --- Админ классы с добавлением Excel и валидаций и фильтров Q---

@admin.register(UserProfile)
class UserProfileAdmin(ExportToExcelMixin, admin.ModelAdmin):
    form = UserProfileAdminForm
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
    actions = [generate_pdf, 'export_as_excel', mark_as_moderator]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            (Q(role='user') | Q(role='moderator')) & ~Q(phone__exact='')
        )


@admin.register(Address)
class AddressAdmin(ExportToExcelMixin, admin.ModelAdmin):
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            (~Q(country='Russia') & ~Q(country='USA')) | Q(index__startswith='9')
        )


@admin.register(Category)
class CategoryAdmin(ExportToExcelMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'photo', 'documentation', 'created_at', 'updated_at')
        }),
    )


@admin.register(Brand)
class BrandAdmin(ExportToExcelMixin, admin.ModelAdmin):
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
class ProductAdmin(ExportToExcelMixin, admin.ModelAdmin):
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
    actions = [generate_pdf, 'export_as_excel', mark_expensive_products]


@admin.register(Color)
class ColorAdmin(ExportToExcelMixin, admin.ModelAdmin):
    list_display = ("name", "color", "created_at")
    search_fields = ("name", "color")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('name', 'color', 'image', 'palette_file', 'created_at', 'updated_at')
        }),
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(ExportToExcelMixin, admin.ModelAdmin):
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
class ProductColorAdmin(ExportToExcelMixin, admin.ModelAdmin):
    list_display = ("product", "color")
    list_filter = ("color", )
    autocomplete_fields = ("product", "color")


@admin.register(Review)
class ReviewAdmin(ExportToExcelMixin, admin.ModelAdmin):
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
class BasketAdmin(ExportToExcelMixin, admin.ModelAdmin):
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
class OrderAdmin(ExportToExcelMixin, admin.ModelAdmin):
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
class BasketOrderAdmin(ExportToExcelMixin, admin.ModelAdmin):
    list_display = ("basket", "order", "count")
    autocomplete_fields = ("basket", "order")


@admin.register(ProductOrder)
class ProductOrderAdmin(ExportToExcelMixin, admin.ModelAdmin):
    list_display = ("product", "product_variant", "order")
    list_filter = ("order", )
    autocomplete_fields = ("product", "product_variant", "order")

