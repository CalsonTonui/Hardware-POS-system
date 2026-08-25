from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    # your existing product fields...


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name