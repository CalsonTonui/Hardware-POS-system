from django.db import models
from products.models import Product
from suppliers.models import Supplier


class Purchase(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    buying_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    purchase_date = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        self.total_amount = (
            self.quantity * self.buying_price
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"