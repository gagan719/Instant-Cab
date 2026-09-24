from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from pricing.models import CabType, Route, FixedPrice, LocalRideSlab
from packages.models import Package, UserPackage
from bookings.models import Booking


class InstantCabSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # User
        self.user = User.objects.create_user(
            username='testcustomer',
            email='test@instantcab.com',
            password='password123',
            first_name='Test',
            last_name='User',
            phone='+91 99999 88888'
        )

        # Cab types
        self.sedan = CabType.objects.create(name='sedan', display_name='Comfort Sedan', capacity=4, luggage_capacity=3)
        self.suv = CabType.objects.create(name='suv', display_name='Prime SUV', capacity=6, luggage_capacity=4)

        # Route & Fixed price
        self.route = Route.objects.create(pickup='Coimbatore', destination='Tiruppur', distance_km=Decimal('55.0'))
        self.fixed_price = FixedPrice.objects.create(route=self.route, cab_type=self.sedan, fixed_fare=Decimal('899.00'))

        # Local ride slab
        self.slab = LocalRideSlab.objects.create(
            cab_type=self.sedan,
            min_distance=Decimal('20.0'),
            max_distance=Decimal('50.0'),
            rate_per_km=Decimal('14.00'),
            base_fare=Decimal('300.00')
        )

        # Package
        self.pkg = Package.objects.create(
            name='Daily Saver',
            price=Decimal('499.00'),
            ride_count=5,
            validity_days=30,
            description='5 rides bundle'
        )

    def test_homepage_renders(self):
        res = self.client.get(reverse('core:home'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Instant')
        self.assertContains(res, 'Tiruppur')

    def test_fixed_prices_catalog(self):
        res = self.client.get(reverse('pricing:fixed_prices'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '899')

    def test_calculate_fare_api_fixed_price(self):
        url = f"{reverse('pricing:api_calculate_fare')}?trip_type=oneway&pickup=Coimbatore&destination=Tiruppur&cab_type=sedan"
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['is_fixed_price'])
        self.assertEqual(data['pricing']['base_fare'], 899.0)

    def test_calculate_fare_api_local_ride(self):
        # Above 20 km: should succeed
        url = f"{reverse('pricing:api_calculate_fare')}?trip_type=local&distance=30&cab_type=sedan"
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])

        # Under 20 km: should error as per PRD
        url_under = f"{reverse('pricing:api_calculate_fare')}?trip_type=local&distance=15&cab_type=sedan"
        res_under = self.client.get(url_under)
        self.assertEqual(res_under.status_code, 400)

    def test_package_list(self):
        res = self.client.get(reverse('packages:list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Daily Saver')

    def test_booking_creation_flow(self):
        self.client.login(username='testcustomer', password='password123')
        post_data = {
            'trip_type': 'oneway',
            'pickup_address': 'Coimbatore',
            'destination_address': 'Tiruppur',
            'distance_km': '55.0',
            'pickup_date': timezone.now().strftime('%Y-%m-%d'),
            'pickup_time': '10:00',
            'cab_type_id': self.sedan.id,
            'passenger_name': 'Test User',
            'passenger_phone': '+91 99999 88888',
            'payment_method': 'cash',
        }
        res = self.client.post(reverse('bookings:book'), post_data)
        self.assertEqual(res.status_code, 302) # Redirects to confirmation
        
        booking = Booking.objects.first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.pickup_address, 'Coimbatore')
        self.assertEqual(booking.total_fare, Decimal('943.95')) # 899 + 5% tax
