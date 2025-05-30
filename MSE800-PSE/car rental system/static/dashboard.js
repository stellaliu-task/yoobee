document.addEventListener('DOMContentLoaded', function() {
 const user = localStorage.getItem('user');
    if (!user) {
        window.location.href = '/';
        return;
    }

    try {
        JSON.parse(user); // Validate user data
    } catch (e) {
        localStorage.removeItem('user');
        window.location.href = '/';
        return;
    }

    // Set default dates (today + 3 days)
    const today = new Date();
    const futureDate = new Date();
    futureDate.setDate(today.getDate() + 3);
    
    // Format dates for input fields
    document.getElementById('dashboard-start-date').value = today.toISOString().slice(0, 16);
    document.getElementById('dashboard-end-date').value = futureDate.toISOString().slice(0, 16);
    
    // Load available cars immediately on page load
    loadAvailableCars();
    
    // Search button handler
    document.getElementById('dashboard-search-btn').addEventListener('click', loadAvailableCars);
    
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', function() {
        localStorage.removeItem('user');
        window.location.href = '/';
    });

    const resultsContainer = document.getElementById('dashboard-results');
    const loadingIndicator = document.getElementById('dashboard-loading');
    const emptyState = document.getElementById('dashboard-no-results');
    
    async function loadAvailableCars() {
    const startDate = document.getElementById('dashboard-start-date').value;
    const endDate = document.getElementById('dashboard-end-date').value;
    const location = document.getElementById('dashboard-location').value || '';
    
    loadingIndicator.style.display = 'block';
    emptyState.style.display = 'none';
    resultsContainer.innerHTML = '';

    try {
        const response = await fetch(`/api/cars/available?start=${encodeURIComponent(startDate)}&end=${encodeURIComponent(endDate)}&location=${encodeURIComponent(location)}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load cars');
        }
        
        const cars = await response.json();
        
        if (!Array.isArray(cars)) {
            throw new Error('Invalid response format');
        }
        
        if (cars.length === 0) {
            emptyState.style.display = 'block';
            return;
        }

        renderCars(cars);
    } catch (error) {
        console.error("Failed to load cars:", error);
        resultsContainer.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                ${error.message || 'Failed to load available cars'}
            </div>
        `;
    } finally {
        loadingIndicator.style.display = 'none';
    }
}

function renderCars(cars) {
    const resultsContainer = document.getElementById('dashboard-results');
    resultsContainer.innerHTML = cars.map(car => `
        <div class="car-card" data-id="${car.id}">
            <div class="car-image-container">
                <img src="${car.image_url}" alt="${car.name}" class="car-image" 
                     onerror="this.onerror=null;this.src='/static/pics/aqua.jpeg'">
                <div class="car-status available">
                    Available
                </div>
            </div>
            <div class="car-info">
                <h3>${car.name}</h3>
                <div class="car-specs">
                    <span><i class="fas fa-gas-pump"></i> ${car.fuel_type}</span>
                    <span><i class="fas fa-cog"></i> ${car.gear_type}</span>
                    <span><i class="fas fa-users"></i> ${car.seats} seats</span>
                </div>
                <div class="car-location">
                    <i class="fas fa-map-marker-alt"></i> ${car.location}
                </div>
                <div class="car-price">
                    $${car.price.toFixed(2)} <small>/day</small>
                    ${car.insurance_price ? `<span class="insurance">+ $${car.insurance_price.toFixed(2)} insurance</span>` : ''}
                </div>
                <button class="book-btn">
                    <i class="fas fa-calendar-check"></i> Book Now
                </button>
            </div>
        </div>
    `).join('');

    // Add event listeners to book buttons
    document.querySelectorAll('.book-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const carId = e.target.closest('.car-card').dataset.id;
            const startDate = document.getElementById('dashboard-start-date').value;
            const endDate = document.getElementById('dashboard-end-date').value;
            bookCar(carId, startDate, endDate);
        });
    });
}

    function arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }

    async function bookCar(carId, startDate, endDate) {
        const user = JSON.parse(localStorage.getItem('user'));
        
        try {
            const response = await fetch('/api/orders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    car_id: carId,
                    start_datetime: startDate,
                    end_datetime: endDate,
                    user_id: user.id
                })
            });
            
            const result = await response.json();
            
            if (result.error) {
                alert(`Booking failed: ${result.error}`);
            } else {
                window.location.href = `/order?order_id=${result.order_id}`;
               // alert(`✅ Booking confirmed!\nOrder ID: ${result.order_id}`);
                //loadAvailableCars(); // Refresh the car list
            }
        } catch (error) {
            console.error('Booking failed:', error);
            alert('Failed to complete booking. Please try again.');
        }
    }
    
    loadAllCars();

    function displayAllCars(cars) {
        const grid = document.getElementById('dashboard-results');
        grid.innerHTML = cars.map(car => `
            <div class="car-card">
                <div class="car-image" style="background-image: url('${getCarImage(car)}')">
                    ${!car.picture ? '<i class="fas fa-car-side"></i>' : ''}
                </div>
                <div class="car-details">
                    <h3>${car.name || 'No Name'}</h3>
                    <div class="availability ${car.available_datetime ? 'available' : 'unavailable'}">
                        ${car.available_datetime ? 
                          `Available: ${formatDate(car.available_datetime)}` : 
                          'Currently unavailable'}
                    </div>
                    <div class="price">$${car.price?.toFixed(2) || '0.00'}/day</div>
                    ${car.available_datetime ? `
                    <button onclick="bookCar(${car.id})" class="book-btn">
                        <i class="fas fa-calendar-check"></i> Book
                    </button>` : ''}
                </div>
            </div>
        `).join('');
    }

    // Helper functions
    function getCarImage(car) {
        if (!car.picture) return '';
        try {
            const bytes = new Uint8Array(car.picture);
            const blob = new Blob([bytes], {type: 'image/jpeg'});
            return URL.createObjectURL(blob);
        } catch (e) {
            console.error("Image processing error:", e);
            return '';
        }
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }

    function showLoading() {
        document.getElementById('dashboard-loading').style.display = 'block';
    }

    function hideLoading() {
        document.getElementById('dashboard-loading').style.display = 'none';
    }

    function showNoResults() {
        document.getElementById('dashboard-no-results').style.display = 'block';
    }
    
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        document.querySelector('.cars-section').prepend(errorDiv);
    }
});

window.bookCar = async function(carId, startDate, endDate) {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
        alert('Please login first');
        window.location.href = '/';
        return;
    }
    
    try {
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                car_id: carId,
                start_datetime: startDate,
                end_datetime: endDate,
                user_id: user.id
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert(`Booking failed: ${result.error}`);
        } else {
            window.location.href = `/order?order_id=${result.order_id}`;
        }
    } catch (error) {
        console.error('Booking failed:', error);
        alert('Failed to complete booking. Please try again.');
    }
};