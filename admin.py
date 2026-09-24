from django.contrib import admin
from .models import Route, CabType, FixedPrice, LocalRideSlab


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('pickup', 'destination', 'distance_km', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('pickup', 'destination')
    list_editable = ('is_active',)


@admin.register(CabType)
class CabTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'capacity', 'luggage_capacity', 'is_active')
    list_filter = ('is_active',)
    list_editable = ('is_active',)


@admin.register(FixedPrice)
class FixedPriceAdmin(admin.ModelAdmin):
    list_display = ('route', 'cab_type', 'fixed_fare', 'is_active')
    list_filter = ('is_active', 'cab_type')
    search_fields = ('route__pickup', 'route__destination')
    list_editable = ('fixed_fare', 'is_active')


@admin.register(LocalRideSlab)
class LocalRideSlabAdmin(admin.ModelAdmin):
    list_display = ('cab_type', 'min_distance', 'max_distance', 'rate_per_km', 'base_fare', 'is_active')
    list_filter = ('is_active', 'cab_type')
    list_editable = ('rate_per_km', 'base_fare', 'is_active')
