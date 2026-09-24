# Instant Cab — Full-Stack Django Cab Booking Platform

Instant Cab is a modern, transparent cab-booking platform engineered with **Python Django**, **SQLite**, and responsive **HTML5/Vanilla CSS/JavaScript**, built strictly in adherence with the **Instant Cab Product Requirements Document (PRD)**.

---

## 🌟 Key Differentiators & Features

1. **Fixed-Price Rides (PRD Section 23A)**:
   - Fares displayed prominently and guaranteed before booking confirmation.
   - Pre-seeded routes:
     - **Coimbatore ➔ Tiruppur**: Sedan ₹899 (55 km)
     - **Coimbatore ➔ Pollachi**: Sedan ₹749 (45 km)
     - **Coimbatore ➔ Mettupalayam**: Sedan ₹699 (35 km)
     - **Coimbatore ➔ Ooty**: Sedan ₹1,499 (85 km)
     - Hatchback and SUV variants also available.

2. **Local Rides Above 20 km (PRD Section 23B)**:
   - Minimum distance gate (>20 km) with progressive tiered slab rates (Sedan ₹14/km, SUV ₹18/km, Hatchback ₹12/km).
   - Zero round-trip return tolls or dead-mileage penalties.
   - Interactive live distance slider and dynamic fare estimator.

3. **Subscription Package Plans (PRD Section 23C)**:
   - **Daily Saver**: ₹499 • 5 rides • 30 days
   - **Monthly Commuter**: ₹1,999 • 20 rides • 30 days
   - **Business Pack**: ₹3,499 • 40 rides • 30 days
   - Dedicated **Package Wallet** with automated one-click ride token redemption during booking.

4. **Interactive Multi-Step Booking Journey (PRD Section 5 & 14)**:
   - Trip-type tabs: Outstation One-Way, Outstation Round-Trip, Local (>20 km).
   - Dynamic real-time AJAX fare estimation (`/pricing/api/calculate-fare/`).
   - Automated driver matching & vehicle assignment.
   - Payment options: UPI, Credit/Debit Card, Cash to Driver, or Package Ride.
   - Instant confirmation with reference ID (e.g., `IC-849201A`) and printable invoice receipt.

5. **Role-Based Portals (PRD Section 16 & 17)**:
   - **Customer Portal**: My Bookings, live trip status timeline, package wallet, printable tax invoices, and ratings/reviews.
   - **Captain / Driver Portal**: Dedicated duty switcher (Available, On Trip, Offline), trip queue, Start Ride, and Complete Ride actions.
   - **Operations Admin Command Center**: Live KPIs (Total Bookings, Active Rides, Completed Trips, Revenue), booking dispatch queue, and driver roster.
   - **Django Admin Interface**: Full ORM CRUD access at `/admin/`.

---

## 🔐 Demo Credentials

The database comes pre-seeded with realistic data:

| Role | Username | Password | Notes |
|---|---|---|---|
| **Operations Admin** | `admin` | `admin123` | Full administrative & operational console access |
| **Demo Customer** | `customer` | `customer123` | Pre-subscribed to Daily Saver package with active & past trips |
| **Demo Captain / Driver** | `karthik_driver` | `driver123` | Assigned to Maruti Dzire (`TN 38 BL 4521`), 4.92★ rating |
| **Demo Captain / Driver 2** | `suresh_driver` | `driver123` | Assigned to Innova Crysta (`TN 38 CC 8904`), 4.88★ rating |

---

## 🚀 How to Run Locally

### 1. Run the Development Server
```bash
python manage.py runserver
```

Open your browser at: **`http://127.0.0.1:8000/`**

### 2. Run Automated Unit Tests
```bash
python manage.py test core
```

### 3. Re-seed Data (Optional)
If you ever want to reset or reload the PRD seed data:
```bash
python seed_data.py
```

---

## 📂 Project Architecture

```
Instant Cab/
├── instant_cab/          # Project settings, WSGI, main URL routing
├── accounts/             # Custom AbstractUser, Authentication, Profiles
├── pricing/              # Routes, FixedPrice, CabType, LocalRideSlab, Fare API
├── packages/             # Package plans, UserPackage wallet, subscription logic
├── drivers/              # Vehicle, Driver models, Duty console, Captain roster
├── bookings/             # Multi-step booking engine, itinerary, trip tracking
├── payments/             # Payments tracking, Tax invoice receipts
├── reviews/              # Ratings, customer feedback, driver reviews
├── core/                 # Home hero widget, About, Contact, FAQ, Admin Dashboard
├── templates/            # HTML5 responsive semantic templates
│   ├── base.html
│   ├── accounts/
│   ├── bookings/
│   ├── core/
│   ├── drivers/
│   ├── packages/
│   ├── payments/
│   ├── pricing/
│   └── reviews/
├── static/
│   ├── css/style.css     # Master design system (palette, glassmorphism, cards)
│   └── js/main.js        # Dynamic AJAX fare calculator & UI toggles
├── db.sqlite3            # SQLite database
├── seed_data.py          # PRD database population script
└── manage.py             # Django CLI
```
