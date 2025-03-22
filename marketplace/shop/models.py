from django.db import models
from django.urls import reverse

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    
from django.contrib.auth.models import User

class UserProfile(TimeStampedModel):
    ROLE_CHOICES = [
        ('consumer', 'Consumer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='consumer')
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Address(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    index = models.CharField(max_length=20)
    
    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

    def __str__(self):
        return f"{self.city}, {self.street}"


class Category(TimeStampedModel):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='categories/')
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name
    
    def get_absolute_url(self): #
        return reverse('category_detail', kwargs={'slug': self.slug}) #


class Brand(TimeStampedModel):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='brands/')
    description = models.TextField()
    
    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='products/')
    slug = models.SlugField(unique=True)
    avg_rating = models.FloatField(default=0.0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    default_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class Color(TimeStampedModel):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20)  # HEX-код или название
    image = models.ImageField(upload_to='colors/', blank=True, null=True)

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"

    def __str__(self):
        return self.name


class ProductVariant(TimeStampedModel):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='variants/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    images = models.JSONField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Вариант товара"
        verbose_name_plural = "Варианты товаров"

    def __str__(self):
        return self.name


class ProductColor(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Цвет товара"
        verbose_name_plural = "Цвета товаров"


class Review(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.FloatField()
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Review by {self.name} on {self.product.name}"


class Basket(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    count = models.PositiveIntegerField()
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"{self.user.username}'s basket"
    
    @classmethod
    def add_to_cart(cls, user, product_variant, count=1):
        basket_item, created = cls.objects.get_or_create(
            user=user, product_variant=product_variant,
            defaults={'count': count, 'product': product_variant.product}
        )
        if not created:
            basket_item.count = f"count + {count}"
            basket_item.save(update_fields=['count'])
        return basket_item


class Order(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    full_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Order by {self.user.username}"


class BasketOrder(TimeStampedModel):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    count = models.PositiveIntegerField()
    
    class Meta:
        verbose_name = "Заказ в корзине"
        verbose_name_plural = "Заказы в корзине"

class ProductOrder(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказах"
