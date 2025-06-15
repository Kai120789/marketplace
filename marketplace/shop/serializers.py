from rest_framework import serializers
from .models import Product, Category, Brand, ProductVariant, Review

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'default_price': {'min_value': 0.01}
        }
    
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Название должно содержать минимум 3 символа")
        return value

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ProductVariant.objects.all(),
                fields=['product', 'color'],
                message="Такой вариант товара уже существует"
            )
        ]

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
    
    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5")
        return value