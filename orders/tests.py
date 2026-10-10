from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomerProfile, SellerProfile
from stores.models import Product, Store
from .models import CartItem, Order


class MarketplaceFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seller_user = User.objects.create_user(
            username='seller1',
            password='SellerPass123'
        )
        cls.seller = SellerProfile.objects.create(user=seller_user)

        cls.store = Store.objects.create(
            name='Test Store',
            owner=cls.seller
        )
        cls.product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.00'),
            stock=5,
            store=cls.store
        )

        customer_user = User.objects.create_user(
            username='customer1',
            password='CustomerPass123'
        )
        cls.customer = CustomerProfile.objects.create(
            user=customer_user,
            phone='09120000000',
            balance=Decimal('50.00')
        )

    def login_customer(self):
        self.client.login(
            username='customer1',
            password='CustomerPass123'
        )

    def login_seller(self):
        self.client.login(
            username='seller1',
            password='SellerPass123'
        )

    def test_checkout_moves_money_and_creates_order(self):
        self.login_customer()
        self.client.post(reverse('add_to_cart', args=[self.product.pk]))

        response = self.client.post(reverse('checkout'))

        self.assertRedirects(response, reverse('order_history'))

        self.customer.refresh_from_db()
        self.store.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('40.00'))
        self.assertEqual(self.store.balance, Decimal('10.00'))
        self.assertEqual(self.product.stock, 4)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(CartItem.objects.count(), 0)

        order = Order.objects.get()
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.total_amount, Decimal('10.00'))

        item = order.orderitem_set.get()
        self.assertEqual(item.price, Decimal('10.00'))
        self.assertEqual(item.quantity, 1)

    def test_checkout_with_insufficient_balance(self):
        self.product.price = Decimal('80.00')
        self.product.save()

        self.login_customer()
        self.client.post(reverse('add_to_cart', args=[self.product.pk]))

        response = self.client.post(reverse('checkout'))

        self.assertRedirects(response, reverse('payment'))
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(CartItem.objects.count(), 1)

        self.customer.refresh_from_db()
        self.store.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('50.00'))
        self.assertEqual(self.store.balance, Decimal('0.00'))

    def test_checkout_requires_enough_stock(self):
        self.login_customer()
        self.client.post(reverse('add_to_cart', args=[self.product.pk]))
        self.client.post(reverse('add_to_cart', args=[self.product.pk]))

        self.product.stock = 1
        self.product.save()

        response = self.client.post(reverse('checkout'))

        self.assertRedirects(response, reverse('cart'))
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(CartItem.objects.count(), 1)

        self.customer.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('50.00'))
        self.assertEqual(self.product.stock, 1)

    def test_quantity_can_be_changed(self):
        self.login_customer()
        self.client.post(reverse('add_to_cart', args=[self.product.pk]))
        item = CartItem.objects.get()

        self.client.post(
            reverse('update_cart_item', args=[item.pk]),
            {'action': 'increase'}
        )
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

        self.client.post(
            reverse('update_cart_item', args=[item.pk]),
            {'action': 'decrease'}
        )
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

        self.client.post(
            reverse('update_cart_item', args=[item.pk]),
            {'action': 'decrease'}
        )
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

        # Quantity can never grow past the remaining stock.
        self.product.stock = 1
        self.product.save()
        self.client.post(
            reverse('update_cart_item', args=[item.pk]),
            {'action': 'increase'}
        )
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

    def test_out_of_stock_product_cannot_be_added(self):
        self.product.stock = 0
        self.product.save()

        self.login_customer()
        response = self.client.post(
            reverse('add_to_cart', args=[self.product.pk])
        )

        self.assertRedirects(response, reverse('cart'))
        self.assertEqual(CartItem.objects.count(), 0)

    def test_seller_cannot_use_the_cart(self):
        self.login_seller()
        response = self.client.post(
            reverse('add_to_cart', args=[self.product.pk])
        )

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(CartItem.objects.count(), 0)
