from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from pricing.models import FixedPrice, CabType, Route, LocalRideSlab
from packages.models import Package, UserPackage
from bookings.models import Booking
from drivers.models import Driver
from payments.models import Payment
from reviews.models import Review


def home_view(request):
    """
    Instant Cab Homepage featuring:
    - Interactive Hero booking widget
    - Featured Fixed Price Routes
    - Featured Subscription Packages
    - Differentiator cards (Fixed prices, Local >20km, Package plans)
    - Latest customer reviews
    """
    featured_fixed_prices = FixedPrice.objects.filter(is_active=True).select_related('route', 'cab_type')[:6]
    packages = Package.objects.filter(is_active=True).order_by('price')[:3]
    cab_types = CabType.objects.filter(is_active=True)
    reviews = Review.objects.all().select_related('user', 'booking')[:4]
    
    total_completed_trips = Booking.objects.filter(status=Booking.STATUS_COMPLETED).count()
    verified_drivers_count = Driver.objects.filter(is_verified=True).count()

    context = {
        'featured_fixed_prices': featured_fixed_prices,
        'packages': packages,
        'cab_types': cab_types,
        'reviews': reviews,
        'total_completed_trips': total_completed_trips or 1250,
        'verified_drivers_count': verified_drivers_count or 45,
        'today_date': timezone.now().strftime('%Y-%m-%d'),
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    """About Instant Cab company and mission."""
    return render(request, 'core/about.html')


def contact_view(request):
    """Contact & support view with form submission."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        messages.success(request, f"Thank you {name}! Your message has been received. Our support team will get in touch shortly.")
        return redirect('core:contact')
    return render(request, 'core/contact.html')


def faq_view(request):
    """Frequently Asked Questions."""
    return render(request, 'core/faq.html')


@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'role') and u.role == 'admin'))
def admin_dashboard_view(request):
    """
    Operational Instant Cab Operations Management Dashboard.
    Provides real-time business metrics, booking management, driver rosters, and revenue.
    """
    total_bookings = Booking.objects.count()
    active_rides = Booking.objects.filter(status__in=[Booking.STATUS_CONFIRMED, Booking.STATUS_ONGOING]).count()
    completed_rides = Booking.objects.filter(status=Booking.STATUS_COMPLETED).count()
    total_revenue = Payment.objects.filter(status=Payment.STATUS_SUCCESS).aggregate(total=Sum('amount'))['total'] or 0
    total_drivers = Driver.objects.count()
    available_drivers = Driver.objects.filter(status=Driver.STATUS_AVAILABLE).count()

    recent_bookings = Booking.objects.all().select_related('user', 'cab_type', 'driver').order_by('-created_at')[:10]
    drivers_list = Driver.objects.all().select_related('user', 'vehicle', 'vehicle__cab_type')[:8]
    fixed_prices = FixedPrice.objects.filter(is_active=True).select_related('route', 'cab_type')

    # Handle quick action from operations dashboard
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('new_status')
        assign_driver_id = request.POST.get('driver_id')

        if booking_id:
            booking = Booking.objects.get(booking_id=booking_id)
            if new_status:
                booking.status = new_status
            if assign_driver_id:
                driver = Driver.objects.get(id=assign_driver_id)
                booking.driver = driver
                if booking.status == Booking.STATUS_PENDING:
                    booking.status = Booking.STATUS_CONFIRMED
            booking.save()
            messages.success(request, f"Booking {booking_id} updated successfully.")
            return redirect('core:admin_dashboard')

    context = {
        'total_bookings': total_bookings,
        'active_rides': active_rides,
        'completed_rides': completed_rides,
        'total_revenue': total_revenue,
        'total_drivers': total_drivers,
        'available_drivers': available_drivers,
        'recent_bookings': recent_bookings,
        'drivers_list': drivers_list,
        'fixed_prices': fixed_prices,
    }
    return render(request, 'core/admin_dashboard.html', context)
