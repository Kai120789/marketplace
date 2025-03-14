from django.contrib import admin
from .models import (
    UserProfile, Address, Category, Brand, Product, Color, ProductVariant, 
    ProductColor, Review, Basket, Order, BasketOrder, ProductOrder
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "phone")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "country", "city", "street", "index", "created_at")
    list_filter = ("country", "city")
    search_fields = ("street", "city", "index")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_at")
    search_fields = ("name", "slug")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "brand", "default_price", "created_at")
    list_filter = ("category", "brand")
    search_fields = ("name", "slug")
    inlines = [ProductVariantInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "created_at")
    search_fields = ("name", "color")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "product", "color", "price", "created_at")
    list_filter = ("color", )
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "color")
    list_filter = ("color", )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "rating", "name", "created_at")
    list_filter = ("created_at", )
    search_fields = ("name", "description")


class BasketOrderInline(admin.TabularInline):
    model = BasketOrder
    extra = 1


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "product_variant", "count", "created_at")
    list_filter = ("user",)
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_price", "created_at")
    list_filter = ("user", "created_at")
    search_fields = ("user__username",)
    inlines = [BasketOrderInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(BasketOrder)
class BasketOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "basket", "order", "count")


@admin.register(ProductOrder)
class ProductOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "product_variant", "order")
    list_filter = ("order", )
