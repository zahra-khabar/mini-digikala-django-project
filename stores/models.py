from django.db import models
from accounts.models import SellerProfile


class Store(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(
        SellerProfile,
        on_delete=models.CASCADE,
        related_name='stores'
    )
    description = models.TextField(blank=True)
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
