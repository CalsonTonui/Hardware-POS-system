from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Purchase
from inventory.models import Inventory

@receiver(post_save, sender=Purchase)
def update_inventory(sender, instance, created, **kwargs):
    if created:
        inventory, created_inventory = Inventory.objects.get_or_create(
            product=instance.product,
            defaults={'quantity': 0}
        )

        inventory.quantity += instance.quantity
        inventory.save()