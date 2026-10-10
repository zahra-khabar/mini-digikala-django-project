from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

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
