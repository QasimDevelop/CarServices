from django.db import models
from store.models import Product, User  # Correct import of User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime

class DeletedOrder(models.Model):
    original_id = models.IntegerField()
    customer_name = models.CharField(max_length=255)
    service_date = models.DateTimeField()
    deleted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'deleted_orders'

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.CharField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'

# Create a user Shipping Address by default when user signs up
def create_shipping(sender, instance, created, **kwargs):
    if created:
        user_shipping = ShippingAddress(user=instance)
        user_shipping.save()

# Automate the profile thing
post_save.connect(create_shipping, sender=User)

# Create Order Model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name="payment_orders")
    amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)
    date_confirmed = models.DateTimeField(blank=True, null=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    slot_time = models.CharField(max_length=255)
    image = models.ImageField(upload_to='uploads/order', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Order - {str(self.id)}'

# Auto Add shipping Date
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    if instance.pk:
        now = datetime.datetime.now()
        obj = sender._default_manager.get(pk=instance.pk)
        if instance.shipped and not obj.shipped:
            instance.date_shipped = now

# Create Order Items Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f'Order Item - {str(self.id)}'

class Slots(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    status = models.BooleanField(default=True)

    class Meta:
        unique_together = ('date', 'start_time')

    def __str__(self):
        return f"{self.date} {self.start_time.strftime('%I:%M %p')}"