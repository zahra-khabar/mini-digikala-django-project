import os
import shutil
import tempfile
from decimal import Decimal
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image as PILImage

from accounts.models import CustomerProfile, SellerProfile
from orders.models import Order, OrderItem
from .models import Category, Product, Store


class StoreManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        owner_user = User.objects.create_user(
            username='owner',
            password='OwnerPass123'
        )
        cls.owner = SellerProfile.objects.create(user=owner_user)
        cls.store = Store.objects.create(
            name='Owner Store',
            owner=cls.owner
        )

        other_user = User.objects.create_user(
            username='other_seller',
            password='OtherPass123'
        )
        cls.other_seller = SellerProfile.objects.create(user=other_user)

        visitor_user = User.objects.create_user(
            username='visitor',
            password='VisitorPass123'
        )
        cls.visitor = CustomerProfile.objects.create(
            user=visitor_user,
            phone='09120000001'
        )

    def login(self, username, password):
        self.client.login(username=username, password=password)

    def test_seller_can_create_store(self):
        self.login('owner', 'OwnerPass123')

        response = self.client.post(
            reverse('create_store'),
            {'name': 'Second Store', 'description': 'More goods'}
        )

        store = Store.objects.get(name='Second Store')
        self.assertRedirects(
            response,
            reverse('store_detail', args=[store.pk])
        )
        self.assertEqual(store.owner, self.owner)

    def test_seller_can_add_product_to_own_store(self):
        self.login('owner', 'OwnerPass123')

        response = self.client.post(
            reverse('add_product', args=[self.store.pk]),
            {
                'name': 'New Product',
                'price': '25.00',
                'stock': '3',
                'description': 'A product'
            }
        )

        product = Product.objects.get(name='New Product')
        self.assertRedirects(
            response,
            reverse('store_detail', args=[self.store.pk])
        )
        self.assertEqual(product.store, self.store)

    def test_other_seller_cannot_add_product(self):
        self.login('other_seller', 'OtherPass123')

        response = self.client.post(
            reverse('add_product', args=[self.store.pk]),
            {'name': 'Sneaky', 'price': '1.00', 'description': ''}
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Product.objects.filter(name='Sneaky').exists()
        )

    def test_customer_cannot_create_store(self):
        self.login('visitor', 'VisitorPass123')

        response = self.client.post(
            reverse('create_store'),
            {'name': 'Not Allowed', 'description': ''}
        )

        self.assertRedirects(response, reverse('customer_panel'))
        self.assertFalse(
            Store.objects.filter(name='Not Allowed').exists()
        )

    def test_owner_can_delete_product(self):
        product = Product.objects.create(
            name='Disposable',
            price=Decimal('5.00'),
            stock=1,
            store=self.store
        )

        self.login('owner', 'OwnerPass123')
        response = self.client.post(
            reverse(
                'delete_product',
                args=[self.store.pk, product.pk]
            )
        )

        self.assertRedirects(
            response,
            reverse('store_detail', args=[self.store.pk])
        )
        self.assertFalse(
            Product.objects.filter(pk=product.pk).exists()
        )

    def test_product_with_orders_cannot_be_deleted(self):
        product = Product.objects.create(
            name='Ordered Item',
            price=Decimal('5.00'),
            stock=1,
            store=self.store
        )
        order = Order.objects.create(
            customer=self.visitor,
            total_amount=Decimal('5.00')
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=Decimal('5.00')
        )

        self.login('owner', 'OwnerPass123')
        response = self.client.post(
            reverse(
                'delete_product',
                args=[self.store.pk, product.pk]
            )
        )

        self.assertRedirects(
            response,
            reverse('store_detail', args=[self.store.pk])
        )
        self.assertTrue(
            Product.objects.filter(pk=product.pk).exists()
        )

    def test_home_search_and_category_filter(self):
        electronics = Category.objects.create(name='Electronics')

        Product.objects.create(
            name='Gaming Laptop',
            price=Decimal('100.00'),
            stock=2,
            store=self.store,
            category=electronics
        )
        Product.objects.create(
            name='Coffee Mug',
            price=Decimal('5.00'),
            stock=3,
            store=self.store
        )

        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Gaming Laptop')
        self.assertContains(response, 'Coffee Mug')

        response = self.client.get(reverse('home'), {'q': 'laptop'})
        self.assertContains(response, 'Gaming Laptop')
        self.assertNotContains(response, 'Coffee Mug')

        response = self.client.get(
            reverse('home'),
            {'category': electronics.pk}
        )
        self.assertContains(response, 'Gaming Laptop')
        self.assertNotContains(response, 'Coffee Mug')

    def test_missing_image_file_falls_back_to_placeholder(self):
        Product.objects.create(
            name='Broken Image Product',
            price=Decimal('1.00'),
            stock=1,
            store=self.store,
            image='products/missing.webp'
        )

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'بدون تصویر')
        self.assertNotContains(response, 'products/missing.webp')

    def test_owner_can_edit_store(self):
        self.login('owner', 'OwnerPass123')

        response = self.client.post(
            reverse('edit_store', args=[self.store.pk]),
            {'name': 'Renamed Store', 'description': 'Updated'}
        )

        self.assertRedirects(
            response,
            reverse('store_detail', args=[self.store.pk])
        )

        self.store.refresh_from_db()
        self.assertEqual(self.store.name, 'Renamed Store')
        self.assertEqual(self.store.description, 'Updated')

    def test_other_seller_cannot_edit_store(self):
        self.login('other_seller', 'OtherPass123')

        response = self.client.post(
            reverse('edit_store', args=[self.store.pk]),
            {'name': 'Hacked Store', 'description': ''}
        )

        self.assertEqual(response.status_code, 403)

        self.store.refresh_from_db()
        self.assertNotEqual(self.store.name, 'Hacked Store')

    def test_seed_demo_is_repeatable(self):
        call_command('seed_demo')
        first_users = User.objects.count()
        first_products = Product.objects.count()

        call_command('seed_demo')

        self.assertEqual(User.objects.count(), first_users)
        self.assertEqual(Product.objects.count(), first_products)
        self.assertTrue(
            CustomerProfile.objects.filter(
                user__username='customer_demo'
            ).exists()
        )
        self.assertTrue(
            Product.objects.filter(
                store__name='دیجی‌استور'
            ).exists()
        )


class ProductImageUploadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        owner_user = User.objects.create_user(
            username='image_owner',
            password='OwnerPass123'
        )
        cls.owner = SellerProfile.objects.create(user=owner_user)
        cls.store = Store.objects.create(
            name='Image Store',
            owner=cls.owner
        )

    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

    def login_owner(self):
        self.client.login(
            username='image_owner',
            password='OwnerPass123'
        )

    def upload(self, name, payload, content_type):
        return SimpleUploadedFile(
            name,
            payload,
            content_type=content_type
        )

    def test_seller_can_upload_a_product_image(self):
        self.login_owner()

        buffer = BytesIO()
        PILImage.new('RGB', (20, 20), 'blue').save(buffer, format='PNG')

        response = self.client.post(
            reverse('add_product', args=[self.store.pk]),
            {
                'name': 'Photo Product',
                'price': '9.00',
                'stock': '1',
                'description': '',
                'image': self.upload(
                    'photo.png', buffer.getvalue(), 'image/png'
                ),
            }
        )

        product = Product.objects.get(name='Photo Product')
        self.assertRedirects(
            response,
            reverse('store_detail', args=[self.store.pk])
        )
        self.assertTrue(product.image.name)
        self.assertTrue(
            product.image.storage.exists(product.image.name)
        )

    def test_oversized_image_is_rejected(self):
        self.login_owner()

        buffer = BytesIO()
        image = PILImage.frombytes(
            'RGB',
            (1600, 1600),
            os.urandom(1600 * 1600 * 3)
        )
        image.save(buffer, format='PNG')

        response = self.client.post(
            reverse('add_product', args=[self.store.pk]),
            {
                'name': 'Big Product',
                'price': '9.00',
                'stock': '1',
                'description': '',
                'image': self.upload(
                    'big.png', buffer.getvalue(), 'image/png'
                ),
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Product.objects.filter(name='Big Product').exists()
        )
        self.assertContains(response, 'حجم تصویر')

    def test_heic_image_is_accepted(self):
        try:
            import pillow_heif  # noqa: F401
        except ImportError:
            self.skipTest('pillow-heif is not installed')

        self.login_owner()

        buffer = BytesIO()
        PILImage.new('RGB', (20, 20), 'orange').save(buffer, format='HEIF')

        response = self.client.post(
            reverse('add_product', args=[self.store.pk]),
            {
                'name': 'HEIC Product',
                'price': '9.00',
                'stock': '1',
                'description': '',
                'image': self.upload(
                    'photo.heic', buffer.getvalue(), 'image/heic'
                ),
            }
        )

        product = Product.objects.get(name='HEIC Product')
        self.assertRedirects(
            response,
            reverse('store_detail', args=[self.store.pk])
        )
        self.assertTrue(product.image.name)
