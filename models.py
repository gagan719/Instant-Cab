from django.db import models


class Route(models.Model):
    pickup = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, help_text="Distance in kilometers")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pickup} → {self.destination} ({self.distance_km} km)"

    class Meta:
        unique_together = ('pickup', 'destination')
        ordering = ['pickup', 'destination']
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'


class CabType(models.Model):
    SEDAN = 'sedan'
    SUV = 'suv'
    HATCHBACK = 'hatchback'
    LUXURY = 'luxury'
    TEMPO = 'tempo'

    TYPE_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (HATCHBACK, 'Hatchback'),
        (LUXURY, 'Luxury'),
        (TEMPO, 'Tempo Traveller'),
    ]

    name = models.CharField(max_length=50, choices=TYPE_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    capacity = models.IntegerField(default=4)
    luggage_capacity = models.IntegerField(default=2, help_text="Number of large bags")
    image = models.FileField(upload_to='cab_types/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = 'Cab Type'
        verbose_name_plural = 'Cab Types'


class FixedPrice(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='fixed_prices')
    cab_type = models.ForeignKey(CabType, on_delete=models.CASCADE, related_name='fixed_prices')
    fixed_fare = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.route} - {self.cab_type} - ₹{self.fixed_fare}"

    class Meta:
        unique_together = ('route', 'cab_type')
        verbose_name = 'Fixed Price'
        verbose_name_plural = 'Fixed Prices'


class LocalRideSlab(models.Model):
    """Pricing slabs for local rides above 20 km."""
    cab_type = models.ForeignKey(CabType, on_delete=models.CASCADE, related_name='local_slabs')
    min_distance = models.DecimalField(max_digits=8, decimal_places=2, help_text="Minimum distance (km)")
    max_distance = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                        help_text="Maximum distance (km), leave blank for unlimited")
    rate_per_km = models.DecimalField(max_digits=8, decimal_places=2)
    base_fare = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def calculate_fare(self, distance_km):
        from decimal import Decimal
        return self.base_fare + (Decimal(str(distance_km)) * self.rate_per_km)

    def __str__(self):
        max_d = f"{self.max_distance} km" if self.max_distance else "∞"
        return f"{self.cab_type} | {self.min_distance} - {max_d} | ₹{self.rate_per_km}/km"

    class Meta:
        ordering = ['cab_type', 'min_distance']
        verbose_name = 'Local Ride Slab'
        verbose_name_plural = 'Local Ride Slabs'
