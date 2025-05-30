from django.db import models
from django.urls import reverse

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

from django.contrib.auth.models import User

class UserProfile(TimeStampedModel):
    ROLE_CHOICES = [
        ('consumer', 'Покупатель'),
        ('seller', 'Продавец'),
        ('admin', 'Администратор'),
    ]

    user = models.OneToOneField(
        User, 
        verbose_name="Пользователь", 
        on_delete=models.CASCADE, 
        related_name="profile"
    )
    phone = models.CharField(
        "Телефон", 
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True
    )
    role = models.CharField(
        "Роль", 
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='consumer'
    )
    avatar = models.ImageField(
        "Аватар", 
        upload_to='avatars/', 
        blank=True, 
        null=True
    )
    resume = models.FileField(
        "Резюме", 
        upload_to='resumes/', 
        blank=True, 
        null=True
    )
    website = models.URLField(
        "Веб-сайт", 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Address(TimeStampedModel):
    user = models.ForeignKey(
        User, 
        verbose_name="Пользователь", 
        on_delete=models.CASCADE
    )
    country = models.CharField(
        "Страна", 
        max_length=100
    )
    city = models.CharField(
        "Город", 
        max_length=100
    )
    street = models.CharField(
        "Улица", 
        max_length=255
    )
    index = models.CharField(
        "Индекс", 
        max_length=20
    )
    map_link = models.URLField(
        "Ссылка на карту", 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

    def __str__(self):
        return f"{self.city}, {self.street}"

class Category(TimeStampedModel):
    name = models.CharField(
        "Название", 
        max_length=255
    )
    photo = models.ImageField(
        "Фото", 
        upload_to='categories/'
    )
    slug = models.SlugField(
        "URL", 
        unique=True
    )
    documentation = models.FileField(
        "Документация", 
        upload_to='category_docs/', 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class Brand(TimeStampedModel):
    name = models.CharField(
        "Название", 
        max_length=255
    )
    photo = models.ImageField(
        "Логотип", 
        upload_to='brands/'
    )
    description = models.TextField(
        "Описание"
    )
    official_website = models.URLField(
        "Официальный сайт", 
        blank=True, 
        null=True
    )
    catalog_pdf = models.FileField(
        "Каталог (PDF)", 
        upload_to='brand_catalogs/', 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.name

class Product(TimeStampedModel):
    name = models.CharField(
        "Название", 
        max_length=255
    )
    photo = models.ImageField(
        "Фото", 
        upload_to='products/'
    )
    slug = models.SlugField(
        "URL", 
        unique=True
    )
    avg_rating = models.FloatField(
        "Средний рейтинг", 
        default=0.0
    )
    category = models.ForeignKey(
        Category, 
        verbose_name="Категория", 
        on_delete=models.CASCADE
    )
    description = models.TextField(
        "Описание"
    )
    brand = models.ForeignKey(
        Brand, 
        verbose_name="Бренд", 
        on_delete=models.CASCADE
    )
    default_price = models.DecimalField(
        "Цена", 
        max_digits=10, 
        decimal_places=2
    )
    manual = models.FileField(
        "Инструкция", 
        upload_to='product_manuals/', 
        blank=True, 
        null=True
    )
    video_url = models.URLField(
        "Видео", 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Color(TimeStampedModel):
    name = models.CharField(
        "Название", 
        max_length=50
    )
    color = models.CharField(
        "HEX-код", 
        max_length=20
    )
    image = models.ImageField(
        "Изображение", 
        upload_to='colors/', 
        blank=True, 
        null=True
    )
    palette_file = models.FileField(
        "Палитра", 
        upload_to='color_palettes/', 
        blank=True, 
        null=True
    )

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"

    def __str__(self):
        return self.name

class ProductVariant(TimeStampedModel):
    name = models.CharField(
        "Название", 
        max_length=255
    )
    photo = models.ImageField(
        "Фото", 
        upload_to='variants/'
    )
    product = models.ForeignKey(
        Product, 
        verbose_name="Товар", 
        on_delete=models.CASCADE
    )
    slug = models.SlugField(
        "URL", 
        unique=True
    )
    color = models.ForeignKey(
        Color, 
        verbose_name="Цвет", 
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category, 
        verbose_name="Категория", 
        on_delete=models.CASCADE
    )
    description = models.TextField(
        "Описание"
    )
    images = models.JSONField(
        "Изображения"
    )
    brand = models.ForeignKey(
        Brand, 
        verbose_name="Бренд", 
        on_delete=models.CASCADE
    )
    price = models.DecimalField(
        "Цена", 
        max_digits=10, 
        decimal_places=2
    )
    technical_drawing = models.FileField(
        "Технический чертеж", 
        upload_to='technical_drawings/', 
        blank=True, 
        null=True
    )
    product_url = models.URLField(
        "Ссылка на товар", 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = "Вариант товара"
        verbose_name_plural = "Варианты товаров"

    def __str__(self):
        return self.name

class ProductColor(TimeStampedModel):
    product = models.ForeignKey(
        Product, 
        verbose_name="Товар", 
        on_delete=models.CASCADE
    )
    color = models.ForeignKey(
        Color, 
        verbose_name="Цвет", 
        on_delete=models.CASCADE
    )
    
    class Meta:
        verbose_name = "Цвет товара"
        verbose_name_plural = "Цвета товаров"

class Review(TimeStampedModel):
    product = models.ForeignKey(
        Product, 
        verbose_name="Товар", 
        on_delete=models.CASCADE
    )
    rating = models.FloatField(
        "Рейтинг"
    )
    name = models.CharField(
        "Имя", 
        max_length=255
    )
    description = models.TextField(
        "Отзыв"
    )
    photo = models.ImageField(
        "Фото", 
        upload_to='review_photos/', 
        blank=True, 
        null=True
    )
    video_review_url = models.URLField(
        "Видео-отзыв", 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Отзыв от {self.name} на {self.product.name}"

class Basket(TimeStampedModel):
    user = models.ForeignKey(
        User, 
        verbose_name="Пользователь", 
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, 
        verbose_name="Товар", 
        on_delete=models.CASCADE
    )
    product_variant = models.ForeignKey(
        ProductVariant, 
        verbose_name="Вариант товара", 
        on_delete=models.CASCADE
    )
    count = models.PositiveIntegerField(
        "Количество"
    )
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"
    
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
    user = models.ForeignKey(
        User, 
        verbose_name="Пользователь", 
        on_delete=models.CASCADE
    )
    address = models.ForeignKey(
        Address, 
        verbose_name="Адрес", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    full_price = models.DecimalField(
        "Общая стоимость", 
        max_digits=10, 
        decimal_places=2
    )
    invoice = models.FileField(
        "Счет", 
        upload_to='invoices/', 
        blank=True, 
        null=True
    )
    tracking_url = models.URLField(
        "Трек-номер", 
        blank=True, 
        null=True
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ пользователя {self.user.username}"

class BasketOrder(TimeStampedModel):
    basket = models.ForeignKey(
        Basket, 
        verbose_name="Корзина", 
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order, 
        verbose_name="Заказ", 
        on_delete=models.CASCADE
    )
    count = models.PositiveIntegerField(
        "Количество"
    )
    
    class Meta:
        verbose_name = "Заказ в корзине"
        verbose_name_plural = "Заказы в корзине"

class ProductOrder(TimeStampedModel):
    product = models.ForeignKey(
        Product, 
        verbose_name="Товар", 
        on_delete=models.CASCADE
    )
    product_variant = models.ForeignKey(
        ProductVariant, 
        verbose_name="Вариант товара", 
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order, 
        verbose_name="Заказ", 
        on_delete=models.CASCADE
    )
    
    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказах"

class iuexam(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название экзамена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    exam_date = models.DateTimeField(verbose_name="Дата проведения экзамена")
    image = models.ImageField(upload_to='exam_images/', verbose_name="Изображение задания")
    users = models.ManyToManyField(User, verbose_name="Пользователи для экзамена")
    is_public = models.BooleanField(default=False, verbose_name="Опубликовано")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Экзамен"
        verbose_name_plural = "Экзамены"