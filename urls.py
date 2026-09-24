from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('history/', views.payment_history_view, name='history'),
    path('receipt/<str:transaction_id>/', views.payment_receipt_view, name='receipt'),
]
