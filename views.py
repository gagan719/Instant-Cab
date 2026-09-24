from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Payment


@login_required
def payment_history_view(request):
    """List of all payments and transactions for the logged in user."""
    payments = Payment.objects.filter(user=request.user).select_related('booking', 'package')
    return render(request, 'payments/history.html', {'payments': payments})


@login_required
def payment_receipt_view(request, transaction_id):
    """View a detailed invoice/receipt for a payment."""
    payment = get_object_or_404(Payment, transaction_id=transaction_id, user=request.user)
    return render(request, 'payments/receipt.html', {'payment': payment})
