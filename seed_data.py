import os
import django
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instant_cab.settings')
django.setup()

from accounts.models import User
from pricing.models import CabType, Route, FixedPrice, LocalRideSlab
from packages.models import Package, UserPackage
from drivers.models import Vehicle, Driver
from bookings.models import Booking
from payments.models import Payment
from reviews.models import Review

print("🌱 Seeding Instant Cab database with realistic PRD data...")

# 1. Create Superuser & Demo Users
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@instantcab.com',
        'first_name': 'System',
        'last_name': 'Administrator',
        'role': User.ROLE_ADMIN,
        'is_staff': True,
        'is_superuser': True,
        'is_verified': True,
        'phone': '+91 98765 43210'
    }
)
admin_user.set_password('admin123')
admin_user.save()

customer_user, _ = User.objects.get_or_create(
    username='customer',
    defaults={
        'email': 'rahul.sharma@example.com',
        'first_name': 'Rahul',
        'last_name': 'Sharma',
        'role': User.ROLE_CUSTOMER,
        'is_verified': True,
        'phone': '+91 98450 12345',
        'address': 'Gandhipuram, Coimbatore, Tamil Nadu'
    }
)
customer_user.set_password('customer123')
customer_user.save()

driver_user1, _ = User.objects.get_or_create(
    username='karthik_driver',
    defaults={
        'email': 'karthik.cab@instantcab.com',
        'first_name': 'Karthik',
        'last_name': 'Ramasamy',
        'role': User.ROLE_DRIVER,
        'is_verified': True,
        'phone': '+91 97890 54321',
        'address': 'RS Puram, Coimbatore'
    }
)
driver_user1.set_password('driver123')
driver_user1.save()

driver_user2, _ = User.objects.get_or_create(
    username='suresh_driver',
    defaults={
        'email': 'suresh.cab@instantcab.com',
        'first_name': 'Suresh',
        'last_name': 'Kumar',
        'role': User.ROLE_DRIVER,
        'is_verified': True,
        'phone': '+91 98940 98765',
        'address': 'Peelamedu, Coimbatore'
    }
)
driver_user2.set_password('driver123')
driver_user2.save()

print("✓ Users created: admin (admin/admin123), customer (customer/customer123), drivers")

# 2. Cab Types
cabs_data = [
    {
        'name': CabType.HATCHBACK,
        'display_name': 'Economy Hatchback',
        'capacity': 4,
        'luggage_capacity': 2,
        'description': 'Pocket-friendly rides for quick getaways and light travel (WagonR, Swift, Tiago).'
    },
    {
        'name': CabType.SEDAN,
        'display_name': 'Comfort Sedan',
        'capacity': 4,
        'luggage_capacity': 3,
        'description': 'Top comfort for intercity & local trips with spacious boot space (Dzire, Etios, Aura).'
    },
    {
        'name': CabType.SUV,
        'display_name': 'Prime SUV',
        'capacity': 6,
        'luggage_capacity': 4,
        'description': 'Extra legroom and high-power hill driving comfort for family trips (Innova, Ertiga, Carens).'
    },
    {
        'name': CabType.LUXURY,
        'display_name': 'Executive Luxury',
        'capacity': 4,
        'luggage_capacity': 3,
        'description': 'Premium corporate rides and VIP hospitality (Camry, Fortuner, BMW).'
    }
]

created_cabs = {}
for cd in cabs_data:
    cab, _ = CabType.objects.get_or_create(name=cd['name'], defaults=cd)
    created_cabs[cd['name']] = cab

print("✓ Cab types created:", list(created_cabs.keys()))

# 3. Vehicles & Drivers
v1, _ = Vehicle.objects.get_or_create(
    registration_number='TN 38 BL 4521',
    defaults={
        'cab_type': created_cabs[CabType.SEDAN],
        'model_name': 'Maruti Suzuki Dzire VXI',
        'color': 'Glacier White',
        'year': 2023
    }
)

d1, _ = Driver.objects.get_or_create(
    user=driver_user1,
    defaults={
        'license_number': 'TN3820190045892',
        'vehicle': v1,
        'experience_years': 6,
        'status': Driver.STATUS_AVAILABLE,
        'rating': Decimal('4.92'),
        'total_trips': 342,
        'current_city': 'Coimbatore'
    }
)

v2, _ = Vehicle.objects.get_or_create(
    registration_number='TN 38 CC 8904',
    defaults={
        'cab_type': created_cabs[CabType.SUV],
        'model_name': 'Toyota Innova Crysta',
        'color': 'Silver Metallic',
        'year': 2022
    }
)

d2, _ = Driver.objects.get_or_create(
    user=driver_user2,
    defaults={
        'license_number': 'TN3820170098451',
        'vehicle': v2,
        'experience_years': 8,
        'status': Driver.STATUS_AVAILABLE,
        'rating': Decimal('4.88'),
        'total_trips': 518,
        'current_city': 'Coimbatore'
    }
)

print("✓ Vehicles and Drivers linked")

# 4. PRD Fixed Price Routes
routes_data = [
    {'pickup': 'Coimbatore', 'destination': 'Tiruppur', 'distance_km': Decimal('55.0'), 'sedan_price': Decimal('899.00')},
    {'pickup': 'Coimbatore', 'destination': 'Pollachi', 'distance_km': Decimal('45.0'), 'sedan_price': Decimal('749.00')},
    {'pickup': 'Coimbatore', 'destination': 'Mettupalayam', 'distance_km': Decimal('35.0'), 'sedan_price': Decimal('699.00')},
    {'pickup': 'Coimbatore', 'destination': 'Ooty', 'distance_km': Decimal('85.0'), 'sedan_price': Decimal('1499.00')},
    {'pickup': 'Coimbatore', 'destination': 'Palakkad', 'distance_km': Decimal('52.0'), 'sedan_price': Decimal('849.00')},
    {'pickup': 'Coimbatore', 'destination': 'Erode', 'distance_km': Decimal('100.0'), 'sedan_price': Decimal('1699.00')},
]

for rd in routes_data:
    r, _ = Route.objects.get_or_create(
        pickup=rd['pickup'],
        destination=rd['destination'],
        defaults={'distance_km': rd['distance_km']}
    )
    # Sedan fixed price (PRD specification)
    FixedPrice.objects.get_or_create(
        route=r,
        cab_type=created_cabs[CabType.SEDAN],
        defaults={'fixed_fare': rd['sedan_price']}
    )
    # SUV fixed price (approx 1.4x)
    FixedPrice.objects.get_or_create(
        route=r,
        cab_type=created_cabs[CabType.SUV],
        defaults={'fixed_fare': round(rd['sedan_price'] * Decimal('1.4'), -1)}
    )
    # Hatchback fixed price (approx 0.85x)
    FixedPrice.objects.get_or_create(
        route=r,
        cab_type=created_cabs[CabType.HATCHBACK],
        defaults={'fixed_fare': round(rd['sedan_price'] * Decimal('0.85'), -1)}
    )

print("✓ PRD Fixed Price Routes populated (Coimbatore to Tiruppur, Pollachi, Mettupalayam, Ooty, etc.)")

# 5. Local Ride Slabs (Above 20 km)
local_slabs = [
    # Sedan
    {'cab_type': created_cabs[CabType.SEDAN], 'min_distance': Decimal('20.0'), 'max_distance': Decimal('50.0'), 'rate_per_km': Decimal('14.00'), 'base_fare': Decimal('300.00')},
    {'cab_type': created_cabs[CabType.SEDAN], 'min_distance': Decimal('50.0'), 'max_distance': None, 'rate_per_km': Decimal('13.00'), 'base_fare': Decimal('250.00')},
    # SUV
    {'cab_type': created_cabs[CabType.SUV], 'min_distance': Decimal('20.0'), 'max_distance': Decimal('50.0'), 'rate_per_km': Decimal('18.00'), 'base_fare': Decimal('450.00')},
    {'cab_type': created_cabs[CabType.SUV], 'min_distance': Decimal('50.0'), 'max_distance': None, 'rate_per_km': Decimal('16.50'), 'base_fare': Decimal('400.00')},
    # Hatchback
    {'cab_type': created_cabs[CabType.HATCHBACK], 'min_distance': Decimal('20.0'), 'max_distance': Decimal('50.0'), 'rate_per_km': Decimal('12.00'), 'base_fare': Decimal('250.00')},
    {'cab_type': created_cabs[CabType.HATCHBACK], 'min_distance': Decimal('50.0'), 'max_distance': None, 'rate_per_km': Decimal('11.00'), 'base_fare': Decimal('200.00')},
]

for ls in local_slabs:
    LocalRideSlab.objects.get_or_create(
        cab_type=ls['cab_type'],
        min_distance=ls['min_distance'],
        defaults=ls
    )

print("✓ Local Ride Slabs configured for journeys above 20 km")

# 6. PRD Package Plans
packages_data = [
    {
        'name': 'Daily Saver',
        'tagline': 'Ideal for weekly frequent commuters & students',
        'price': Decimal('499.00'),
        'ride_count': 5,
        'validity_days': 30,
        'discount_percentage': 25,
        'description': 'Enjoy 5 rides with guaranteed zero surge pricing and quick priority driver pickup.',
        'features': [
            '5 Rides included',
            'Valid for 30 days',
            'Zero surge pricing guaranteed',
            'Free cancellation up to 1 hr before ride',
            'Priority customer support'
        ]
    },
    {
        'name': 'Monthly Commuter',
        'tagline': 'Most Popular — Best value for working professionals',
        'price': Decimal('1999.00'),
        'ride_count': 20,
        'validity_days': 30,
        'discount_percentage': 35,
        'description': 'Save big on your daily work travel. High priority allocation with AC comfort.',
        'features': [
            '20 Rides included',
            'Valid for 30 days',
            'Dedicated top-rated captains',
            'Advance 24-hr scheduling',
            'Transferable wallet balance'
        ]
    },
    {
        'name': 'Business Pack',
        'tagline': 'Designed for executives, field teams & frequent travellers',
        'price': Decimal('3499.00'),
        'ride_count': 40,
        'validity_days': 30,
        'discount_percentage': 45,
        'description': 'Ultimate corporate mobility package with GST invoicing and 40 flexible rides.',
        'features': [
            '40 Rides included',
            'Valid for 30 days',
            'GST business tax invoice ready',
            'Free ride rescheduling anytime',
            'Executive sedan & SUV access'
        ]
    }
]

created_packages = []
for p_data in packages_data:
    pkg, _ = Package.objects.get_or_create(name=p_data['name'], defaults=p_data)
    created_packages.append(pkg)

print("✓ PRD Subscription Packages created: Daily Saver, Monthly Commuter, Business Pack")

# 7. Customer active subscription
up1, _ = UserPackage.objects.get_or_create(
    user=customer_user,
    package=created_packages[0],
    defaults={
        'rides_total': 5,
        'rides_remaining': 4,
        'expiry_date': timezone.now() + timedelta(days=28)
    }
)

# 8. Sample Completed & Confirmed Bookings
b1, _ = Booking.objects.get_or_create(
    booking_id='IC-849201A',
    defaults={
        'user': customer_user,
        'trip_type': Booking.TRIP_TYPE_ONEWAY,
        'pickup_address': 'Gandhipuram Central Bus Stand, Coimbatore',
        'destination_address': 'Old Bus Stand, Tiruppur',
        'distance_km': Decimal('55.0'),
        'pickup_date': (timezone.now() - timedelta(days=2)).date(),
        'pickup_time': '09:30:00',
        'cab_type': created_cabs[CabType.SEDAN],
        'driver': d1,
        'passenger_name': 'Rahul Sharma',
        'passenger_phone': '+91 98450 12345',
        'base_fare': Decimal('899.00'),
        'taxes_and_tolls': Decimal('45.00'),
        'total_fare': Decimal('944.00'),
        'is_fixed_price': True,
        'payment_method': 'upi',
        'is_paid': True,
        'status': Booking.STATUS_COMPLETED
    }
)

Payment.objects.get_or_create(
    transaction_id='TXN-IC-849201A',
    defaults={
        'user': customer_user,
        'booking': b1,
        'amount': Decimal('944.00'),
        'payment_method': 'UPI',
        'status': Payment.STATUS_SUCCESS,
        'notes': 'Fixed fare Coimbatore to Tiruppur'
    }
)

Review.objects.get_or_create(
    booking=b1,
    defaults={
        'user': customer_user,
        'driver': d1,
        'rating': 5,
        'comment': 'Exceptional ride experience! Driver Karthik was very punctual, car was pristine clean, and the fixed fare of ₹899 had zero hidden surprises.'
    }
)

# Active confirmed booking
b2, _ = Booking.objects.get_or_create(
    booking_id='IC-912384B',
    defaults={
        'user': customer_user,
        'trip_type': Booking.TRIP_TYPE_ONEWAY,
        'pickup_address': 'Coimbatore Airport (CJB)',
        'destination_address': 'Charing Cross, Ooty',
        'distance_km': Decimal('85.0'),
        'pickup_date': (timezone.now() + timedelta(days=1)).date(),
        'pickup_time': '11:00:00',
        'cab_type': created_cabs[CabType.SEDAN],
        'driver': d1,
        'passenger_name': 'Rahul Sharma',
        'passenger_phone': '+91 98450 12345',
        'base_fare': Decimal('1499.00'),
        'taxes_and_tolls': Decimal('75.00'),
        'total_fare': Decimal('1574.00'),
        'is_fixed_price': True,
        'payment_method': 'upi',
        'is_paid': True,
        'status': Booking.STATUS_CONFIRMED
    }
)

print("✓ Sample bookings, payments, and reviews created successfully")
print("🎉 Seeding completed 100%!")
