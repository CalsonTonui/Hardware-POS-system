from django.db import models


class Product(models.Model):

    CATEGORY_CHOICES = [
        ('Hardware', 'Hardware'),
        ('Timber', 'Timber'),
        ('Metals', 'Metals'),
        ('Furniture', 'Furniture'),
        ('Electrical', 'Electrical'),
        ('Plumbing', 'Plumbing'),
        ('Paint', 'Paint'),
        ('Other', 'Other'),
    ]

    UNIT_CHOICES = [
        ('Piece', 'Piece'),
        ('Bag', 'Bag'),
        ('Box', 'Box'),
        ('Kg', 'Kg'),
        ('Metre', 'Metre'),
        ('Foot', 'Foot'),
        ('Litre', 'Litre'),
        ('Set', 'Set'),
        ('Pair', 'Pair'),
        ('Other', 'Other'),
    ]

    name = models.CharField(
        max_length=200
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='Hardware'
    )

    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default='Piece'
    )

    barcode = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    buying_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.name