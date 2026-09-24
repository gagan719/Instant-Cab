from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'payment_type', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_type', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'user__username', 'booking__booking_id')
