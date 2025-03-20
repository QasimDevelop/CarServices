from django.contrib import admin
from .models import DeletedOrder, ShippingAddress, Order, OrderItem,Slots
from django.contrib.auth.models import User


# Register the model on the admin section thing
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Slots)
admin.site.register(DeletedOrder)
# Create an OrderItem Inline
class OrderItemInline(admin.StackedInline):
	model = OrderItem
	extra = 0

# Extend our Order Model
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered", "date_confirmed", "date_shipped"]  # Add other read-only fields if necessary
    fields = [
        "user",
        "amount_paid",
        "confirmed",
        "date_confirmed",
        "shipped",
        "date_shipped",
        "slot_time",
        "image",
        "description"
    ]
    list_display = ("id", "user", "amount_paid", "date_ordered", "confirmed", "shipped")
    search_fields = ["user__username", "id"]
    inlines = [OrderItemInline]

# Unregister Order Model
admin.site.unregister(Order)

# Re-Register our Order AND OrderAdmin
admin.site.register(Order, OrderAdmin)