from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random


# =========================================================
# USER MODEL
# =========================================================

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        ('storekeeper', 'Storekeeper'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Force user to change password on next login
    must_change_password = models.BooleanField(
        default=False,
        help_text="Force user to change password on next login"
    )

    def __str__(self):
        return self.get_full_name() or self.username


# =========================================================
# USER CREATION OTP
# =========================================================

class UserCreationOTP(models.Model):
    """Temporary OTP for verifying new user creation."""

    METHOD_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
    ]

    username = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, default='cashier')
    is_active = models.BooleanField(default=True)

    otp_code = models.CharField(max_length=6, default='')
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='email')

    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)

    def __str__(self):
        return f"OTP for {self.username} via {self.method}"


# =========================================================
# ACTIVITY LOG
# =========================================================

class ActivityLog(models.Model):
    """Track important system actions for accountability."""

    ACTION_CHOICES = [
        # Authentication
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('failed_login', 'Failed Login Attempt'),

        # Sales
        ('sale_created', 'Sale Created'),
        ('sale_deleted', 'Sale Deleted'),

        # Products
        ('product_added', 'Product Added'),
        ('product_edited', 'Product Edited'),
        ('product_deleted', 'Product Deleted'),

        # Inventory
        ('purchase_created', 'Purchase Created'),
        ('stock_adjusted', 'Stock Adjusted'),

        # Users
        ('user_added', 'User Added'),
        ('user_edited', 'User Edited'),
        ('user_deleted', 'User Deleted'),
        ('user_activated', 'User Activated'),
        ('user_deactivated', 'User Deactivated'),
        ('password_changed', 'Password Changed'),

        # Expenses
        ('expense_added', 'Expense Added'),
        ('expense_edited', 'Expense Edited'),
        ('expense_deleted', 'Expense Deleted'),

        # Suppliers
        ('supplier_added', 'Supplier Added'),
        ('supplier_edited', 'Supplier Edited'),
        ('supplier_deleted', 'Supplier Deleted'),

        # Services
        ('service_added', 'Service Added'),
        ('service_edited', 'Service Edited'),
        ('service_deleted', 'Service Deleted'),

        # Settings
        ('settings_updated', 'Settings Updated'),

        # Other
        ('other', 'Other Action'),
    ]

    user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        help_text='User who performed the action'
    )

    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        db_index=True
    )

    description = models.TextField(
        help_text='Detailed description of what happened'
    )

    target_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Type of object affected (Product, Sale, User, etc.)'
    )

    target_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='ID of the object affected'
    )

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True
    )

    user_agent = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        indexes = [
            models.Index(fields=['-timestamp', 'action']),
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        user_display = self.user.username if self.user else 'Anonymous'
        return f"{user_display} - {self.get_action_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def get_action_color(self):
        """Return a color class for UI badges."""
        if 'deleted' in self.action:
            return 'danger'
        elif 'added' in self.action or 'created' in self.action:
            return 'success'
        elif 'edited' in self.action or 'updated' in self.action:
            return 'warning'
        elif 'login' in self.action or 'logout' in self.action:
            return 'info'
        elif 'failed' in self.action:
            return 'danger'
        return 'secondary'

    def get_action_icon(self):
        """Return a Bootstrap icon class."""
        icons = {
            'login': 'bi-box-arrow-in-right',
            'logout': 'bi-box-arrow-right',
            'failed_login': 'bi-exclamation-triangle-fill',
            'sale_created': 'bi-cart-check-fill',
            'sale_deleted': 'bi-cart-x-fill',
            'product_added': 'bi-box-seam-fill',
            'product_edited': 'bi-pencil-square',
            'product_deleted': 'bi-trash-fill',
            'purchase_created': 'bi-cart-plus-fill',
            'stock_adjusted': 'bi-arrow-repeat',
            'user_added': 'bi-person-plus-fill',
            'user_edited': 'bi-person-gear',
            'user_deleted': 'bi-person-x-fill',
            'user_activated': 'bi-person-check-fill',
            'user_deactivated': 'bi-person-slash',
            'password_changed': 'bi-shield-lock-fill',
            'expense_added': 'bi-cash-stack',
            'expense_edited': 'bi-pencil-square',
            'expense_deleted': 'bi-trash-fill',
            'supplier_added': 'bi-truck',
            'supplier_edited': 'bi-pencil-square',
            'supplier_deleted': 'bi-trash-fill',
            'service_added': 'bi-tools',
            'service_edited': 'bi-pencil-square',
            'service_deleted': 'bi-trash-fill',
            'settings_updated': 'bi-gear-fill',
        }
        return icons.get(self.action, 'bi-activity')