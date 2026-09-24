from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Route, CabType, FixedPrice, LocalRideSlab


def fixed_prices_view(request):
    """Catalog of fixed-price routes."""
    fixed_prices = FixedPrice.objects.filter(is_active=True).select_related('route', 'cab_type').order_by('route__pickup', 'route__destination')
    cab_types = CabType.objects.filter(is_active=True)
    
    # Optional search filter
    q = request.GET.get('q', '').strip()
    selected_cab = request.GET.get('cab_type', '')
    
    if q:
        fixed_prices = fixed_prices.filter(
            route__pickup__icontains=q
        ) | fixed_prices.filter(
            route__destination__icontains=q
        )
    if selected_cab:
        fixed_prices = fixed_prices.filter(cab_type__name=selected_cab)

    context = {
        'fixed_prices': fixed_prices,
        'cab_types': cab_types,
        'q': q,
        'selected_cab': selected_cab,
    }
    return render(request, 'pricing/fixed_prices.html', context)


def local_ride_view(request):
    """Information and dynamic fare estimator for local rides above 20 km."""
    cab_types = CabType.objects.filter(is_active=True)
    slabs = LocalRideSlab.objects.filter(is_active=True).select_related('cab_type').order_by('cab_type', 'min_distance')
    return render(request, 'pricing/local_ride.html', {
        'cab_types': cab_types,
        'slabs': slabs
    })


@require_GET
def calculate_fare_api(request):
    """
    Dynamic fare calculation API based on trip type, pickup, destination, distance, and cab type.
    """
    trip_type = request.GET.get('trip_type', 'oneway')
    pickup = request.GET.get('pickup', '').strip()
    destination = request.GET.get('destination', '').strip()
    cab_type_name = request.GET.get('cab_type', 'sedan')
    try:
        distance_km = Decimal(str(request.GET.get('distance', '35')))
    except Exception:
        distance_km = Decimal('35')

    try:
        cab_type = CabType.objects.get(name=cab_type_name, is_active=True)
    except CabType.DoesNotExist:
        cab_type = CabType.objects.filter(is_active=True).first()

    if not cab_type:
        return JsonResponse({'error': 'No cab type available'}, status=400)

    # 1. Check for Fixed Price match if pickup and destination are provided
    is_fixed = False
    base_fare = Decimal('0')
    route_obj = None

    if pickup and destination:
        route = Route.objects.filter(
            pickup__iexact=pickup,
            destination__iexact=destination,
            is_active=True
        ).first()
        
        if not route:
            # Try reverse route match if applicable
            route = Route.objects.filter(
                pickup__iexact=destination,
                destination__iexact=pickup,
                is_active=True
            ).first()

        if route:
            route_obj = route
            distance_km = route.distance_km
            fixed_price = FixedPrice.objects.filter(
                route=route,
                cab_type=cab_type,
                is_active=True
            ).first()

            if fixed_price:
                is_fixed = True
                base_fare = fixed_price.fixed_fare

    # 2. If not fixed price, calculate according to trip type & slabs
    if not is_fixed:
        if trip_type == 'local':
            # Local ride logic: minimum distance requirement is 20 km
            if distance_km < Decimal('20'):
                return JsonResponse({
                    'error': 'Local rides require a minimum distance greater than 20 km. Standard city rules apply for shorter trips.',
                    'min_distance_required': 20
                }, status=400)

            slab = LocalRideSlab.objects.filter(
                cab_type=cab_type,
                is_active=True,
                min_distance__lte=distance_km
            ).order_by('-min_distance').first()

            if slab:
                base_fare = slab.calculate_fare(distance_km)
            else:
                # Default fallback calculation
                rate = Decimal('14.00') if cab_type.name == 'sedan' else (Decimal('18.00') if cab_type.name == 'suv' else Decimal('12.00'))
                base_fare = Decimal('300.00') + (distance_km * rate)
        elif trip_type == 'roundtrip':
            # Round-trip calculation (2x distance with 10% round-trip savings)
            rate = Decimal('13.50') if cab_type.name == 'sedan' else (Decimal('17.00') if cab_type.name == 'suv' else Decimal('11.50'))
            base_fare = (distance_km * Decimal('2') * rate) + Decimal('400.00')
        else:
            # Standard One-Way outstation
            rate = Decimal('14.00') if cab_type.name == 'sedan' else (Decimal('18.00') if cab_type.name == 'suv' else Decimal('12.00'))
            base_fare = (distance_km * rate) + Decimal('250.00')

    # Round fares to nearest 10
    base_fare = round(base_fare, 2)
    toll_and_taxes = round(base_fare * Decimal('0.05'), 2) # 5% GST & service
    total_fare = base_fare + toll_and_taxes

    return JsonResponse({
        'success': True,
        'is_fixed_price': is_fixed,
        'distance_km': float(distance_km),
        'cab_type': {
            'id': cab_type.id,
            'name': cab_type.name,
            'display_name': cab_type.display_name,
            'capacity': cab_type.capacity,
            'luggage_capacity': cab_type.luggage_capacity,
        },
        'pricing': {
            'base_fare': float(base_fare),
            'taxes_and_tolls': float(toll_and_taxes),
            'total_fare': float(total_fare),
        },
        'route_id': route_obj.id if route_obj else None
    })
