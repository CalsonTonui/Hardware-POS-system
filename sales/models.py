from django.db import models
from django.conf import settings
from products.models import Product


class Sale(models.Model):

    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('M-Pesa', 'M-Pesa'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_made'
    )

    quantity = models.PositiveIntegerField(default=1)

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='Cash'
    )

    mpesa_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    sale_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.product:
            self.selling_price = self.product.selling_price
        self.total_amount = self.quantity * self.selling_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"