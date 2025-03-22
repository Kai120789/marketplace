from django.contrib import admin
from .models import (
    UserProfile, Address, Category, Brand, Product, Color, ProductVariant, 
    ProductColor, Review, Basket, Order, BasketOrder, ProductOrder
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "phone")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('user', 'phone', 'role', 'created_at', 'updated_at')
        }),
    )
    autocomplete_fields = ("user",)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "country", "city", "street", "index", "created_at")
    list_filter = ("country", "city")
    search_fields = ("street", "city", "index")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ('user', 'country', 'city', 'street', 'index', 'created_at', 'updated_at')
        }),
    )
    autocomplete_fields = ("user",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    readonly_fields = ("created_at", "updated_at")

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "default_price", "created_at")
    list_filter = ("category", "brand")
    search_fields = ("name", "slug")
    inlines = [ProductVariantInline]
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("category", "brand")

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "created_at")
    search_fields = ("name", "color")
    readonly_fields = ("created_at", "updated_at")

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "color", "price", "created_at")
    list_filter = ("color", )
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("product", "color")

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ("product", "color")
    list_filter = ("color", )
    autocomplete_fields = ("product", "color")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "rating", "name", "created_at")
    list_filter = ("created_at", )
    search_fields = ("name", "description")
    autocomplete_fields = ("product",)

class BasketOrderInline(admin.TabularInline):
    model = BasketOrder
    extra = 1

@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "product_variant", "count", "created_at")
    list_filter = ("user",)
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("user", "product", "product_variant")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "full_price", "created_at")
    list_filter = ("user", "created_at")
    search_fields = ("user__username",)
    inlines = [BasketOrderInline]
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("user",)

@admin.register(BasketOrder)
class BasketOrderAdmin(admin.ModelAdmin):
    list_display = ("basket", "order", "count")
    autocomplete_fields = ("basket", "order")

@admin.register(ProductOrder)
class ProductOrderAdmin(admin.ModelAdmin):
    list_display = ("product", "product_variant", "order")
    list_filter = ("order", )
    autocomplete_fields = ("product", "product_variant", "order")
