from django.db import models


class SystemSettings(models.Model):

    # ==============================
    # BUSINESS INFORMATION
    # ==============================

    business_name = models.CharField(
        max_length=200,
        default='Hardware POS'
    )

    business_phone = models.CharField(
        max_length=30,
        blank=True
    )

    business_email = models.EmailField(
        blank=True
    )

    business_address = models.TextField(
        blank=True
    )

    business_location = models.CharField(
        max_length=200,
        blank=True
    )


    # ==============================
    # SYSTEM SETTINGS
    # ==============================

    currency = models.CharField(
        max_length=10,
        default='KSh'
    )

    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    low_stock_threshold = models.PositiveIntegerField(
        default=5
    )


    # ==============================
    # RECEIPT SETTINGS
    # ==============================

    receipt_footer = models.CharField(
        max_length=255,
        default='Thank you for shopping with us.'
    )

    show_business_phone = models.BooleanField(
        default=True
    )

    show_business_address = models.BooleanField(
        default=True
    )


    # ==============================
    # NOTIFICATIONS
    # ==============================

    low_stock_notifications = models.BooleanField(
        default=True
    )

    out_of_stock_notifications = models.BooleanField(
        default=True
    )


    # ==============================
    # SYSTEM
    # ==============================

    updated_at = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):
        return self.business_name