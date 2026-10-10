from django.db import models
from accounts.models import CustomerProfile


class CartItem(models.Model):
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'stores.Product',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'stores.Product',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
