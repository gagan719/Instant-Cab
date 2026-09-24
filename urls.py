from django.urls import path
from . import views

app_name = 'pricing'

urlpatterns = [
    path('fixed-prices/', views.fixed_prices_view, name='fixed_prices'),
    path('local-ride/', views.local_ride_view, name='local_ride'),
    path('api/calculate-fare/', views.calculate_fare_api, name='api_calculate_fare'),
]
