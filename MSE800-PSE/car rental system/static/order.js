document.addEventListener('DOMContentLoaded', function() {
    // Get order details from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const orderId = urlParams.get('order_id');
    
    if (!orderId) {
        window.location.href = '/dashboard';
        return;
    }

    // Fetch order details
    fetchOrderDetails(orderId);

    // Setup event listeners
    document.getElementById('print-receipt').addEventListener('click', printReceipt);
    document.getElementById('back-to-dashboard').addEventListener('click', () => {
        window.location.href = '/dashboard';
    });

    // Logout button
    document.getElementById('logout-btn').addEventListener('click', function() {
        localStorage.removeItem('user');
        window.location.href = '/';
    });
});

async function fetchOrderDetails(orderId) {
    try {
        const response = await fetch(`/api/orders/${orderId}`);
        if (!response.ok) throw new Error('Failed to fetch order details');
        
        const order = await response.json();
        displayOrderDetails(order);
    } catch (error) {
        console.error('Error fetching order:', error);
        alert('Failed to load order details. Please try again.');
        window.location.href = '/dashboard';
    }
}

function displayOrderDetails(order) {
    // Basic order info
    document.getElementById('order-id').textContent = order.id;
    
    // Safely handle created_at (fallback to current time if not available)
    const orderDate = order.created_at ? new Date(order.created_at) : new Date();
    document.getElementById('order-date').textContent = 
        `Order Date: ${orderDate.toLocaleDateString()} at ${orderDate.toLocaleTimeString()}`;
    
    // Car details
    document.getElementById('car-name').textContent = order.car.name;
    document.getElementById('car-image').src = `/api/cars/${order.car.id}/image`;
    document.getElementById('car-fuel-type').textContent = order.car.fuel_type;
    document.getElementById('car-gear-type').textContent = order.car.gear_type;
    document.getElementById('car-seats').textContent = order.car.seats;
    
    // Rental details
    document.getElementById('pickup-location').textContent = order.car.location;
    document.getElementById('pickup-date').textContent = new Date(order.start_datetime).toLocaleString();
    document.getElementById('return-date').textContent = new Date(order.end_datetime).toLocaleString();
    
    // Calculate duration
    const start = new Date(order.start_datetime);
    const end = new Date(order.end_datetime);
    const duration = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
    document.getElementById('rental-duration').textContent = duration;
    
    // Price details
    document.getElementById('base-price').textContent = (order.car.price * duration).toFixed(2);
    document.getElementById('insurance-price').textContent = (order.car.insurance_price * duration).toFixed(2);
    document.getElementById('taxes-fees').textContent = (order.car.price * duration * 0.1).toFixed(2); // 10% tax
    
    const totalPrice = (order.car.price + order.car.insurance_price) * duration * 1.1;
    document.getElementById('total-price').textContent = totalPrice.toFixed(2);
}

function printReceipt() {
    window.print();
}