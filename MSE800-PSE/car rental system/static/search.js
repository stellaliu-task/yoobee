document.addEventListener('DOMContentLoaded', function() {
    // Set default dates (today + 3 days)
    const today = new Date();
    const futureDate = new Date();
    futureDate.setDate(today.getDate() + 3);
    
    document.getElementById('start-date').value = formatDateTime(today);
    document.getElementById('end-date').value = formatDateTime(futureDate);
    
    // Search button handler
    document.getElementById('search-btn').addEventListener('click', searchCars);
    
    async function searchCars() {
        const location = document.getElementById('location').value.trim();
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        // Validate inputs
        if (!startDate || !endDate) {
            alert('Please select both pickup and return dates');
            return;
        }
        
        if (new Date(startDate) >= new Date(endDate)) {
            alert('Return date must be after pickup date');
            return;
        }
        
        // Show loading state
        document.getElementById('loading').style.display = 'block';
        document.getElementById('no-results').style.display = 'none';
        document.getElementById('results-grid').innerHTML = '';
        
        try {
            const response = await fetch(`/api/cars/available?start=${encodeURIComponent(startDate)}&end=${encodeURIComponent(endDate)}&location=${encodeURIComponent(location)}`);
            const cars = await response.json();
            
            document.getElementById('loading').style.display = 'none';
            
            if (!Array.isArray(cars)) {
                showError(cars.error || 'Invalid response from server');
                return;
            }
            
            if (cars.length === 0) {
                document.getElementById('no-results').style.display = 'block';
                return;
            }
            
            displayResults(cars, startDate, endDate);
        } catch (error) {
            document.getElementById('loading').style.display = 'none';
            showError('Failed to search for cars. Please try again.');
            console.error('Search error:', error);
        }
    }
    
    function displayResults(cars, startDate, endDate) {
        const resultsGrid = document.getElementById('results-grid');
        resultsGrid.innerHTML = '';
    
        cars.forEach(car => {
            const carCard = document.createElement('div');
            carCard.className = 'car-card';
            carCard.innerHTML = `
                <div class="car-image-container">
                    ${car.picture_base64 ? 
                        `<img src="data:image/jpeg;base64,${car.picture_base64}" alt="${car.name}" class="car-image">` : 
                        `<div class="no-image"><i class="fas fa-car"></i></div>`}
                </div>
                <div class="car-details">
                    <h3>${car.name}</h3>
                    <div class="car-meta">
                        <span><i class="fas fa-gas-pump"></i> ${car.fuel_type}</span>
                        <span><i class="fas fa-cog"></i> ${car.gear_type}</span>
                        <span><i class="fas fa-users"></i> ${car.seats}</span>
                    </div>
                    <div class="car-meta">
                        <span><i class="fas fa-map-marker-alt"></i> ${car.location}</span>
                    </div>
                    <div class="price">
                        $${car.price.toFixed(2)} <small>/day</small>
                        <small>+ $${car.insurance_price.toFixed(2)} insurance</small>
                    </div>
                    <button class="book-btn" onclick="bookCar(${car.id}, '${startDate}', '${endDate}')">
                        <i class="fas fa-calendar-check"></i> Book Now
                    </button>
                </div>
            `;
            resultsGrid.appendChild(carCard);
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
    
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        document.getElementById('results-container').prepend(errorDiv);
    }
    
    function formatDateTime(date) {
        const pad = num => num.toString().padStart(2, '0');
        return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
    }
});

// Global booking function
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
            //alert(`✅ Booking confirmed!\nOrder ID: ${result.order_id}`);
            //window.location.href = '/dashboard';
        }
    } catch (error) {
        console.error('Booking failed:', error);
        alert('Failed to complete booking. Please try again.');
    }
};