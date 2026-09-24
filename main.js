/**
 * INSTANT CAB - CLIENT-SIDE LOGIC & REAL-TIME FARE CALCULATOR
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Menu Toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const navLinks = document.getElementById('navLinks');
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', function () {
      navLinks.classList.toggle('show');
    });
  }

  // 2. Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.4s ease';
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });

  // 3. Dynamic Interactive Booking Widget
  setupFareCalculator();
});

function setupFareCalculator() {
  const form = document.getElementById('bookingForm') || document.getElementById('heroBookingForm');
  if (!form) return;

  const tripTabs = document.querySelectorAll('.trip-tab-btn');
  const tripTypeInput = document.getElementById('trip_type');
  const returnDateGroup = document.getElementById('returnDateGroup');
  const pickupInput = document.getElementById('pickup_address');
  const destInput = document.getElementById('destination_address');
  const distanceInput = document.getElementById('distance_km');
  const cabTypeInputs = document.querySelectorAll('input[name="cab_type_radio"]') || [];
  const cabTypeIdHidden = document.getElementById('cab_type_id');

  // Preview elements
  const fareDisplay = document.getElementById('displayFare');
  const fareBadge = document.getElementById('displayFareBadge');
  const baseFareDisplay = document.getElementById('displayBaseFare');
  const taxDisplay = document.getElementById('displayTax');
  const distanceNotice = document.getElementById('distanceNotice');
  const distanceDisplay = document.getElementById('displayDistance');

  // Trip Tabs Switcher
  tripTabs.forEach(tab => {
    tab.addEventListener('click', function () {
      tripTabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      const selectedType = this.getAttribute('data-trip-type');
      if (tripTypeInput) tripTypeInput.value = selectedType;

      if (returnDateGroup) {
        if (selectedType === 'roundtrip') {
          returnDateGroup.style.display = 'block';
        } else {
          returnDateGroup.style.display = 'none';
        }
      }

      if (distanceNotice) {
        if (selectedType === 'local') {
          distanceNotice.style.display = 'block';
          if (distanceInput && parseFloat(distanceInput.value) < 20) {
            distanceInput.value = 25;
          }
        } else {
          distanceNotice.style.display = 'none';
        }
      }

      recalculateFare();
    });
  });

  // Location inputs or distance change
  if (pickupInput) pickupInput.addEventListener('change', recalculateFare);
  if (destInput) destInput.addEventListener('change', recalculateFare);
  if (distanceInput) distanceInput.addEventListener('input', recalculateFare);

  // Cab type selection cards
  const cabCards = document.querySelectorAll('.cab-option-card');
  cabCards.forEach(card => {
    card.addEventListener('click', function () {
      cabCards.forEach(c => c.classList.remove('selected'));
      this.classList.add('selected');
      const radio = this.querySelector('input[type="radio"]');
      if (radio) {
        radio.checked = true;
        if (cabTypeIdHidden) cabTypeIdHidden.value = radio.value;
      }
      recalculateFare();
    });
  });

  function recalculateFare() {
    const tripType = tripTypeInput ? tripTypeInput.value : 'oneway';
    const pickup = pickupInput ? pickupInput.value.trim() : '';
    const dest = destInput ? destInput.value.trim() : '';
    const distance = distanceInput ? distanceInput.value : '35';

    // Get selected cab type
    let selectedCabName = 'sedan';
    const selectedCard = document.querySelector('.cab-option-card.selected');
    if (selectedCard) {
      selectedCabName = selectedCard.getAttribute('data-cab-name') || 'sedan';
    }

    // Call dynamic backend API
    const url = `/pricing/api/calculate-fare/?trip_type=${encodeURIComponent(tripType)}&pickup=${encodeURIComponent(pickup)}&destination=${encodeURIComponent(dest)}&distance=${encodeURIComponent(distance)}&cab_type=${encodeURIComponent(selectedCabName)}`;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          if (fareDisplay) {
            fareDisplay.textContent = `₹${Math.round(data.pricing.total_fare).toLocaleString('en-IN')}`;
          }
          if (baseFareDisplay) {
            baseFareDisplay.textContent = `₹${Math.round(data.pricing.base_fare).toLocaleString('en-IN')}`;
          }
          if (taxDisplay) {
            taxDisplay.textContent = `₹${Math.round(data.pricing.taxes_and_tolls).toLocaleString('en-IN')}`;
          }
          if (distanceDisplay) {
            distanceDisplay.textContent = `${data.distance_km} km`;
          }
          if (distanceInput && data.is_fixed_price) {
            distanceInput.value = data.distance_km;
          }

          if (fareBadge) {
            if (data.is_fixed_price) {
              fareBadge.className = 'badge badge-fixed';
              fareBadge.innerHTML = '⚡ Verified Fixed Fare';
            } else if (tripType === 'local') {
              fareBadge.className = 'badge badge-success';
              fareBadge.innerHTML = '📍 Local Ride (>20 km)';
            } else {
              fareBadge.className = 'badge badge-info';
              fareBadge.innerHTML = '🛣 Standard Outstation';
            }
          }
        } else if (data.error) {
          if (fareBadge) {
            fareBadge.className = 'badge badge-warning';
            fareBadge.innerHTML = data.error;
          }
        }
      })
      .catch(err => {
        console.error('Fare calculation error:', err);
      });
  }

  // Trigger initial calculation
  recalculateFare();
}
