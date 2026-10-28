from django.db import models
from django.utils import timezone
from datetime import timedelta


class SystemSettings(models.Model):

    # ==============================
    # BUSINESS INFORMATION
    # ==============================

    business_name = models.CharField(max_length=200, default='Hardware POS')
    business_phone = models.CharField(max_length=30, blank=True)
    business_email = models.EmailField(blank=True)
    business_address = models.TextField(blank=True)
    business_location = models.CharField(max_length=200, blank=True)

    # ==============================
    # SYSTEM SETTINGS
    # ==============================

    currency = models.CharField(max_length=10, default='KSh')

    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    low_stock_threshold = models.PositiveIntegerField(default=5)

    # ==============================
    # RECEIPT SETTINGS
    # ==============================

    receipt_footer = models.CharField(
        max_length=255,
        default='Thank you for shopping with us.'
    )

    show_business_phone = models.BooleanField(default=True)
    show_business_address = models.BooleanField(default=True)

    # ==============================
    # NOTIFICATIONS
    # ==============================

    low_stock_notifications = models.BooleanField(default=True)
    out_of_stock_notifications = models.BooleanField(default=True)

    # ==============================
    # BACKUP SETTINGS (NEW)
    # ==============================

    last_backup_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time the database was backed up'
    )

    backup_reminder_days = models.PositiveIntegerField(
        default=7,
        help_text='Remind admin if no backup in this many days'
    )

    # ==============================
    # SYSTEM
    # ==============================

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name

    def days_since_last_backup(self):
        """Return the number of days since the last backup, or None if never."""
        if not self.last_backup_date:
            return None
        delta = timezone.now() - self.last_backup_date
        return delta.days

    def backup_is_due(self):
        """Return True if the backup reminder should show."""
        days = self.days_since_last_backup()

        # Never backed up = always due
        if days is None:
            return True

        return days >= self.backup_reminder_days

    def mark_backup_done(self):
        """Record a backup now."""
        self.last_backup_date = timezone.now()
        self.save(update_fields=['last_backup_date', 'updated_at'])

    def next_backup_due_date(self):
        """When the next backup is due."""
        if not self.last_backup_date:
            return timezone.now()
        return self.last_backup_date + timedelta(days=self.backup_reminder_days)