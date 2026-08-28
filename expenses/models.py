from django.db import models


class Expense(models.Model):

    EXPENSE_TITLE_CHOICES = [
        ('Shop Rent', 'Shop Rent'),
        ('Electricity Bill', 'Electricity Bill'),
        ('Water Bill', 'Water Bill'),
        ('Internet Subscription', 'Internet Subscription'),
        ('Transport Expense', 'Transport Expense'),
        ('Fuel', 'Fuel'),
        ('Staff Salary', 'Staff Salary'),
        ('Casual Labour', 'Casual Labour'),
        ('Equipment Repair', 'Equipment Repair'),
        ('Computer Repair', 'Computer Repair'),
        ('Printer Repair', 'Printer Repair'),
        ('CCTV Maintenance', 'CCTV Maintenance'),
        ('Cleaning Supplies', 'Cleaning Supplies'),
        ('Office Supplies', 'Office Supplies'),
        ('Packaging Materials', 'Packaging Materials'),
        ('Stationery', 'Stationery'),
        ('Airtime', 'Airtime'),
        ('Bank Charges', 'Bank Charges'),
        ('M-Pesa Charges', 'M-Pesa Charges'),
        ('Business Permit', 'Business Permit'),
        ('Licences', 'Licences'),
        ('Security Services', 'Security Services'),
        ('Delivery Charges', 'Delivery Charges'),
        ('Advertising', 'Advertising'),
        ('Marketing', 'Marketing'),
        ('Refreshments', 'Refreshments'),
        ('Lunch Allowance', 'Lunch Allowance'),
        ('Equipment Purchase', 'Equipment Purchase'),
        ('Software Subscription', 'Software Subscription'),
        ('Miscellaneous Expense', 'Miscellaneous Expense'),
    ]

    CATEGORY_CHOICES = [
        ('Rent', 'Rent'),
        ('Utilities', 'Utilities'),
        ('Transport', 'Transport'),
        ('Salaries', 'Salaries'),
        ('Maintenance', 'Maintenance'),
        ('Supplies', 'Supplies'),
        ('Communication', 'Communication'),
        ('Banking', 'Banking'),
        ('Licences', 'Licences'),
        ('Marketing', 'Marketing'),
        ('Security', 'Security'),
        ('Other', 'Other'),
    ]

    title = models.CharField(
        max_length=200,
        choices=EXPENSE_TITLE_CHOICES
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    description = models.TextField(
        blank=True
    )

    expense_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-expense_date', '-created_at']