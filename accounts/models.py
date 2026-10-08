from django.db import models
from django.contrib.auth.models import User


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
