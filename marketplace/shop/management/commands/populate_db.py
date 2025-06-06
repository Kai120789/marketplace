from django.core.management.base import BaseCommand
from faker import Faker
import random
from shop.models import UserProfile, Address, Category, Brand, Product, Color, ProductVariant, ProductColor, Review, Basket, Order, BasketOrder, ProductOrder
from django.contrib.auth.models import User

# Инициализация Faker с русской локализацией
fake = Faker('ru_RU')

# Списки для категорий, брендов и цветов
CATEGORIES = [
    "Куртки", "Футболки", "Штаны", "Обувь", "Шапки", "Рюкзаки", "Аксессуары", "Худи", "Джинсы", "Ветровки"
]

BRANDS = {
    "Supreme": "Supreme — культовый бренд уличной моды, основанный в Нью-Йорке. Известен своими ограниченными коллекциями и коллаборациями с известными брендами.",
    "Palace": "Palace — британский бренд уличной одежды, сочетающий в себе элементы скейт-культуры и моды. Популярен благодаря своему уникальному стилю.",
    "Off-White": "Off-White — бренд, созданный Вирджилом Абло, сочетающий в себе уличную моду и высокую моду. Известен своими графическими принтами и необычными дизайнами.",
    "Balenciaga": "Balenciaga — люксовый бренд, известный своими инновационными дизайнами и смелыми решениями в моде. Сочетает в себе уличный стиль и высокую моду.",
    "Stone Island": "Stone Island — итальянский бренд, специализирующийся на технологичной одежде. Известен своими инновационными материалами и уникальным дизайном.",
    "The North Face": "The North Face — американский бренд, специализирующийся на одежде и снаряжении для активного отдыха. Популярен благодаря своей надежности и функциональности.",
    "Adidas": "Adidas — один из ведущих мировых брендов спортивной одежды и обуви. Известен своими инновационными технологиями и стильным дизайном.",
    "Nike": "Nike — мировой лидер в производстве спортивной одежды и обуви. Популярен благодаря своим технологичным решениям и вдохновляющей философии.",
    "Puma": "Puma — известный бренд спортивной одежды и обуви, сочетающий в себе стиль и функциональность. Популярен среди спортсменов и любителей уличной моды.",
    "Reebok": "Reebok — бренд спортивной одежды и обуви, известный своими инновационными технологиями и стильным дизайном. Популярен среди любителей фитнеса и уличной моды.",
}

COLORS = [
    {"name": "Черный", "color": "#000000"},
    {"name": "Белый", "color": "#FFFFFF"},
    {"name": "Красный", "color": "#FF0000"},
    {"name": "Синий", "color": "#0000FF"},
    {"name": "Зеленый", "color": "#00FF00"},
    {"name": "Желтый", "color": "#FFFF00"},
    {"name": "Серый", "color": "#808080"},
    {"name": "Оранжевый", "color": "#FFA500"},
    {"name": "Фиолетовый", "color": "#800080"},
    {"name": "Розовый", "color": "#FFC0CB"},
]

# Дополнительные данные для новых полей
AVATAR_URLS = [
    "https://randomuser.me/api/portraits/men/1.jpg",
    "https://randomuser.me/api/portraits/women/1.jpg",
    "https://randomuser.me/api/portraits/men/2.jpg",
    "https://randomuser.me/api/portraits/women/2.jpg",
]

RESUME_FILES = [
    "resumes/sample1.pdf",
    "resumes/sample2.docx",
    "resumes/sample3.pdf",
]

WEBSITES = [
    "https://example.com",
    "https://portfolio.example.com",
    "https://linkedin.com/in/example",
]

MAP_LINKS = [
    "https://maps.google.com/?q=55.7558,37.6176",
    "https://maps.google.com/?q=59.9343,30.3351",
    "https://maps.google.com/?q=54.9833,73.3667",
]

DOCUMENTATION_FILES = [
    "category_docs/doc1.pdf",
    "category_docs/doc2.docx",
    "category_docs/doc3.pdf",
]

BRAND_WEBSITES = [
    "https://www.supremenewyork.com",
    "https://www.palaceskateboards.com",
    "https://www.off---white.com",
    "https://www.balenciaga.com",
]

CATALOG_FILES = [
    "brand_catalogs/catalog1.pdf",
    "brand_catalogs/catalog2.pdf",
]

MANUAL_FILES = [
    "product_manuals/manual1.pdf",
    "product_manuals/manual2.pdf",
]

VIDEO_URLS = [
    "https://youtu.be/example1",
    "https://youtu.be/example2",
    "https://vimeo.com/example",
]

PALETTE_FILES = [
    "color_palettes/palette1.pdf",
    "color_palettes/palette2.jpg",
]

TECHNICAL_DRAWINGS = [
    "technical_drawings/drawing1.pdf",
    "technical_drawings/drawing2.dwg",
]

PRODUCT_URLS = [
    "https://example.com/product1",
    "https://example.com/product2",
]

REVIEW_PHOTOS = [
    "review_photos/photo1.jpg",
    "review_photos/photo2.jpg",
]

REVIEW_VIDEOS = [
    "https://youtu.be/review1",
    "https://vimeo.com/review2",
]

INVOICE_FILES = [
    "invoices/invoice1.pdf",
    "invoices/invoice2.pdf",
]

TRACKING_URLS = [
    "https://tracking.example.com/123",
    "https://tracking.example.com/456",
]

# Шаблоны для названий продуктов
PRODUCT_NAMES = [
    "{} {} {}",
    "{} {} с {}",
    "{} {} в стиле {}",
    "{} {} для {}",
]

# Шаблоны для описаний продуктов
PRODUCT_DESCRIPTIONS = [
    "Стильный и удобный {} от бренда {}. Идеально подходит для {}.",
    "{} {} - это сочетание комфорта и моды. Подходит для {}.",
    "{} {} - это must-have для любого модника. Подходит для {}.",
]

# Шаблоны для комментариев
REVIEW_COMMENTS = [
    "Отличный товар! Очень доволен покупкой.",
    "Качество на высоте, всем рекомендую.",
    "Товар соответствует описанию, доставка быстрая.",
    "Не понравилось качество, ожидал большего.",
    "Отличный выбор для повседневной носки.",
    "Стильно и удобно, всем советую.",
]

class Command(BaseCommand):
    help = 'Populates the database with fake data'

    def handle(self, *args, **kwargs):
        self.create_users(20)
        self.create_categories()
        self.create_brands()
        self.create_products(50)
        self.create_colors()
        self.create_product_variants()
        self.create_product_colors()
        self.create_reviews(200)
        self.create_baskets(50)
        self.create_orders(30)
        self.create_basket_orders(100)
        self.create_product_orders(100)

    def create_users(self, number):
        for _ in range(number):
            user = User.objects.create(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password=fake.password()
            )
            if not UserProfile.objects.filter(user=user).exists():
                UserProfile.objects.create(
                    user=user,
                    phone=fake.phone_number(),
                    role=random.choice(['consumer', 'seller', 'admin']),
                    avatar=random.choice(AVATAR_URLS),
                    resume=random.choice(RESUME_FILES),
                    website=random.choice(WEBSITES)
                )
            if not Address.objects.filter(user=user).exists():
                Address.objects.create(
                    user=user,
                    country="Россия",
                    city=fake.city_name(),
                    street=fake.street_name(),
                    index=fake.postcode(),
                    map_link=random.choice(MAP_LINKS)
                )

    def create_categories(self):
        for category in CATEGORIES:
            Category.objects.create(
                name=category,
                photo='https://media.istockphoto.com/id/1186050470/ru/%D1%84%D0%BE%D1%82%D0%BE/%D1%87%D0%B5%D1%80%D0%BD%D0%B0%D1%8F-%D1%84%D1%83%D1%82%D0%B1%D0%BE%D0%BB%D0%BA%D0%B0-%D0%BD%D0%B0-%D0%B1%D0%B5%D0%BB%D0%BE%D0%BC-%D1%84%D0%BE%D0%BD%D0%B5.jpg?s=1024x1024&w=is&k=20&c=wtMmmHJ2jTTf5hMICBlagNJdlfbZfU7GVZb4Uq_ijB8=',
                slug=fake.unique.slug(),
                documentation=random.choice(DOCUMENTATION_FILES)
            )

    def create_brands(self):
        for brand_name, brand_description in BRANDS.items():
            Brand.objects.create(
                name=brand_name,
                photo='https://cdn.thebrandingjournal.com/wp-content/uploads/2019/05/chanel_logo_the_branding_journal.jpg.webp',
                description=brand_description,
                official_website=random.choice(BRAND_WEBSITES),
                catalog_pdf=random.choice(CATALOG_FILES)
            )

    def create_products(self, number):
        categories = list(Category.objects.all())
        brands = list(Brand.objects.all())
        for _ in range(number):
            category = random.choice(categories)
            brand = random.choice(brands)
            name_template = random.choice(PRODUCT_NAMES)
            description_template = random.choice(PRODUCT_DESCRIPTIONS)

            product_name = name_template.format(
                category.name,
                brand.name,
                fake.word().capitalize()
            )
            product_description = description_template.format(
                category.name,
                brand.name,
                fake.word().capitalize()
            )

            Product.objects.create(
                name=product_name,
                photo='https://aristocratlondon.co.uk/cdn/shop/files/b_d3c3768a-fcd7-4d2a-b04d-22a24974174c.jpg?v=1698671595&width=1440',
                slug=fake.unique.slug(),
                avg_rating=round(random.uniform(3.0, 5.0), 1),
                category=category,
                description=product_description,
                brand=brand,
                default_price=random.uniform(1000.0, 10000.0),
                manual=random.choice(MANUAL_FILES),
                video_url=random.choice(VIDEO_URLS)
            )

    def create_colors(self):
        for color in COLORS:
            Color.objects.create(
                name=color["name"],
                color=color["color"],
                image='colors/default.jpg',
                palette_file=random.choice(PALETTE_FILES)
            )

    def create_product_variants(self):
        products = list(Product.objects.all())
        colors = list(Color.objects.all())
        for product in products:
            num_variants = random.randint(2, 4)
            for i in range(num_variants):
                color = random.choice(colors)
                variant_name = f"{product.name} ({color.name})"
                variant_description = f"Вариант {product.name} в цвете {color.name}. {product.description}"
                
                ProductVariant.objects.create(
                    name=variant_name,
                    photo=product.photo,
                    product=product,
                    slug=f"{product.slug}-{i+1}",
                    color=color,
                    category=product.category,
                    description=variant_description,
                    images={'images': ['https://colapsar.ru/upload/resize_cache/iblock/286/480_480_1/edkrinl60nxw2ina2u8q7uf6tai45woz.jpg' for _ in range(4)]},
                    brand=product.brand,
                    price=random.uniform(1000.0, 10000.0),
                    technical_drawing=random.choice(TECHNICAL_DRAWINGS),
                    product_url=random.choice(PRODUCT_URLS))
                

    def create_product_colors(self):
        products = list(Product.objects.all())
        colors = list(Color.objects.all())
        for product in products:
            for _ in range(random.randint(1, 3)):
                ProductColor.objects.create(
                    product=product,
                    color=random.choice(colors)
                )

    def create_reviews(self, number):
        products = list(Product.objects.all())
        for _ in range(number):
            Review.objects.create(
                product=random.choice(products),
                rating=round(random.uniform(3.0, 5.0), 1),
                name=fake.first_name(),
                description=random.choice(REVIEW_COMMENTS),
                photo=random.choice(REVIEW_PHOTOS),
                video_review_url=random.choice(REVIEW_VIDEOS))
            

    def create_baskets(self, number):
        users = list(User.objects.all())
        products = list(Product.objects.all())
        variants = list(ProductVariant.objects.all())
        for _ in range(number):
            Basket.objects.create(
                user=random.choice(users),
                product=random.choice(products),
                product_variant=random.choice(variants),
                count=random.randint(1, 10))
            

    def create_orders(self, number):
        users = list(User.objects.all())
        addresses = list(Address.objects.all())
        for _ in range(number):
            Order.objects.create(
                user=random.choice(users),
                address=random.choice(addresses),
                full_price=random.uniform(5000.0, 50000.0),
                invoice=random.choice(INVOICE_FILES),
                tracking_url=random.choice(TRACKING_URLS))
            

    def create_basket_orders(self, number):
        baskets = list(Basket.objects.all())
        orders = list(Order.objects.all())
        for _ in range(number):
            BasketOrder.objects.create(
                basket=random.choice(baskets),
                order=random.choice(orders),
                count=random.randint(1, 5))
            

    def create_product_orders(self, number):
        products = list(Product.objects.all())
        variants = list(ProductVariant.objects.all())
        orders = list(Order.objects.all())
        for _ in range(number):
            ProductOrder.objects.create(
                product=random.choice(products),
                product_variant=random.choice(variants),
                order=random.choice(orders))
            