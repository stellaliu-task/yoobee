document.addEventListener('DOMContentLoaded', function() {
    // Toggle between login and register forms
    const loginToggle = document.getElementById('login-toggle');
    const registerToggle = document.getElementById('register-toggle');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    loginToggle.addEventListener('click', function() {
        this.classList.add('active');
        registerToggle.classList.remove('active');
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
        clearErrors();
    });
    
    registerToggle.addEventListener('click', function() {
        this.classList.add('active');
        loginToggle.classList.remove('active');
        registerForm.classList.add('active');
        loginForm.classList.remove('active');
        clearErrors();
    });

    // Clear error messages
    function clearErrors() {
        document.getElementById('login-error').textContent = '';
        document.getElementById('register-error').textContent = '';
    }

    // Handle login form submission
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;
        const errorElement = document.getElementById('login-error');
        
        // Basic validation
        if (!email || !password) {
            errorElement.textContent = 'Please fill in all fields';
            return;
        }

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Store user data and redirect to dashboard
                localStorage.setItem('user', JSON.stringify(data.user));
                window.location.href = '/dashboard';
            } else {
                errorElement.textContent = data.error || 'Login failed. Please check your credentials.';
                // Clear any invalid user data
                localStorage.removeItem('user');
            }
        } catch (err) {
            errorElement.textContent = 'Network error. Please try again later.';
            console.error('Login error:', err);
            localStorage.removeItem('user');
        }
    });
    
    // Handle register form submission
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const email = document.getElementById('register-email').value.trim();
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const errorElement = document.getElementById('register-error');
        
        // Validation
        if (!email || !password || !confirmPassword) {
            errorElement.textContent = 'Please fill in all fields';
            return;
        }

        if (password !== confirmPassword) {
            errorElement.textContent = 'Passwords do not match';
            return;
        }

        if (password.length < 8) {
            errorElement.textContent = 'Password must be at least 8 characters';
            return;
        }

        try {
            // Register the user
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Auto-login after successful registration
                const loginResponse = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password })
                });
                
                const loginData = await loginResponse.json();
                
                if (loginResponse.ok) {
                    localStorage.setItem('user', JSON.stringify(loginData.user));
                    window.location.href = '/dashboard';
                } else {
                    errorElement.textContent = 'Registration successful! Please login with your credentials.';
                }
            } else {
                errorElement.textContent = data.error || 'Registration failed. Please try again.';
            }
        } catch (err) {
            errorElement.textContent = 'Network error. Please try again later.';
            console.error('Registration error:', err);
        }
    });

    // Only check auth status if we're not already on the login page
    if (window.location.pathname !== '/') {
        checkAuthStatus();
    }
});

// Check authentication status
function checkAuthStatus() {
    const user = localStorage.getItem('user');
    if (user) {
        try {
            // Validate the user object
            const userObj = JSON.parse(user);
            if (userObj && userObj.id && userObj.email) {
                // Only redirect if we're not already on the dashboard
                if (window.location.pathname !== '/dashboard') {
                    window.location.href = '/dashboard';
                }
            } else {
                // Invalid user data, clear it
                localStorage.removeItem('user');
            }
        } catch (e) {
            // Invalid JSON, clear it
            localStorage.removeItem('user');
        }
    } else if (window.location.pathname !== '/') {
        // No user and not on login page, redirect to login
        window.location.href = '/';
    }
}