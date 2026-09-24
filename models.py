import uuid
from django.db import models
from django.conf import settings
from bookings.models import Booking
from packages.models import Package, UserPackage


def generate_txn_id():
    return f"TXN-{uuid.uuid4().hex[:12].upper()}"


class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    PAYMENT_TYPE_BOOKING = 'booking'
    PAYMENT_TYPE_PACKAGE = 'package'

    PAYMENT_TYPE_CHOICES = [
        (PAYMENT_TYPE_BOOKING, 'Ride Booking'),
        (PAYMENT_TYPE_PACKAGE, 'Package Purchase'),
    ]

    transaction_id = models.CharField(max_length=50, unique=True, default=generate_txn_id, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default=PAYMENT_TYPE_BOOKING)
    
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    user_package = models.ForeignKey(UserPackage, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='UPI')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUCCESS)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} - ₹{self.amount} ({self.get_status_display()})"
