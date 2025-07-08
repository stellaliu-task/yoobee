document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const loggedOutSection = document.getElementById('loggedOut');
    const loggedInSection = document.getElementById('loggedIn');
    const usernameDisplay = document.getElementById('usernameDisplay');
    const mainContent = document.getElementById('mainContent');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const authForms = document.getElementById('authForms');
    const addBookForm = document.getElementById('addBookForm');
    const bookList = document.getElementById('bookList');
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const updateProfileForm = document.getElementById('updateProfileForm');
    const profileInfo = document.getElementById('profileInfo');

    // API Base URL
    const API_BASE_URL = 'http://localhost:5000/api';

    // Initialize the app
    initApp();

    // Event Listeners
    loginBtn.addEventListener('click', () => showAuthForm('login'));
    registerBtn.addEventListener('click', () => showAuthForm('register'));
    logoutBtn.addEventListener('click', logout);
    
    // Tab switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            const tabId = tab.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Login form submission
    document.getElementById('loginFormElement').addEventListener('submit', async function(e) {
        e.preventDefault();
        await handleLogin();
    });

    // Register form submission
    document.getElementById('registerFormElement').addEventListener('submit', async function(e) {
        e.preventDefault();
        await handleRegister();
    });

    // Add book form submission
    document.getElementById('addBookForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await handleAddBook();
    });

    // Update profile form submission
    document.getElementById('updateProfileForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await handleUpdateProfile();
    });

    // Functions
    async function initApp() {
        const isAuthenticated = await checkAuthStatus();
        if (isAuthenticated) {
            await loadBooks();
            await loadProfile();
        }
    }

    function showAuthForm(formType) {
        authForms.classList.remove('hidden');
        loginForm.classList.add('hidden');
        registerForm.classList.add('hidden');
        
        if (formType === 'login') {
            loginForm.classList.remove('hidden');
        } else {
            registerForm.classList.remove('hidden');
        }
    }

    function hideAuthForms() {
        authForms.classList.add('hidden');
    }

    async function checkAuthStatus() {
        try {
            showLoading('login', true);
            const response = await fetch(`${API_BASE_URL}/users/me`, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const user = await response.json();
                if (user) {
                    loggedIn(user.username);
                    return true;
                }
            }
            loggedOut();
            return false;
        } catch (error) {
            console.error('Error checking auth status:', error);
            loggedOut();
            return false;
        } finally {
            showLoading('login', false);
        }
    }

    function loggedIn(username) {
        loggedOutSection.classList.add('hidden');
        loggedInSection.classList.remove('hidden');
        usernameDisplay.textContent = username;
        mainContent.classList.remove('hidden');
        hideAuthForms();
    }

    function loggedOut() {
        loggedOutSection.classList.remove('hidden');
        loggedInSection.classList.add('hidden');
        mainContent.classList.add('hidden');
    }

    async function handleLogin() {
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        
        if (!username || !password) {
            showError('login', 'Please fill in all fields');
            return;
        }

        try {
            showLoading('login', true);
            const response = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    username: username, 
                    password: password 
                }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                await initApp();
            } else {
                throw new Error(data.error || 'Login failed');
            }
        } catch (error) {
            showError('login', error.message);
            console.error('Login error:', error);
        } finally {
            showLoading('login', false);
        }
    }

    async function handleRegister() {
        const username = document.getElementById('regUsername').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        
        if (!username || !email || !password) {
            showError('register', 'Please fill in all fields');
            return;
        }

        if (password.length < 6) {
            showError('register', 'Password must be at least 6 characters');
            return;
        }

        try {
            showLoading('register', true);
            const response = await fetch(`${API_BASE_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    username: username, 
                    email: email, 
                    password: password 
                }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showAuthForm('login');
                alert('Registration successful! Please login.');
            } else {
                throw new Error(data.error || 'Registration failed');
            }
        } catch (error) {
            showError('register', error.message);
            console.error('Registration error:', error);
        } finally {
            showLoading('register', false);
        }
    }

    async function logout() {
        try {
            showLoading('logout', true);
            await fetch(`${API_BASE_URL}/logout`, {
                method: 'POST',
                credentials: 'include'
            });
            loggedOut();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            showLoading('logout', false);
        }
    }

    async function loadBooks() {
        try {
            showLoading('books', true);
            const response = await fetch(`${API_BASE_URL}/users/me/books`, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const books = await response.json();
                displayBooks(books);
            } else {
                throw new Error('Failed to load books');
            }
        } catch (error) {
            console.error('Error loading books:', error);
            showError('books', error.message);
        } finally {
            showLoading('books', false);
        }
    }

    function displayBooks(books) {
        bookList.innerHTML = '';
        
        if (!books || books.length === 0) {
            bookList.innerHTML = '<p>No books found. Add some books to get started!</p>';
            return;
        }
        
        books.forEach(book => {
            const bookCard = document.createElement('div');
            bookCard.className = 'book-card';
            
            const statusMap = {
                'want_to_read': 'Want to Read',
                'reading': 'Currently Reading',
                'read': 'Read'
            };
            
            bookCard.innerHTML = `
                <h3>${book.title}</h3>
                ${book.author ? `<p>Author: ${book.author}</p>` : ''}
                <p>Status: ${statusMap[book.status] || book.status}</p>
                ${book.description ? `<p>${book.description}</p>` : ''}
            `;
            
            bookList.appendChild(bookCard);
        });
    }

    async function handleAddBook() {
        const title = document.getElementById('title').value;
        const author = document.getElementById('author').value;
        const description = document.getElementById('description').value;
        const status = document.getElementById('status').value;
        
        if (!title || !status) {
            showError('addBook', 'Title and status are required');
            return;
        }

        try {
            showLoading('addBook', true);
            const response = await fetch(`${API_BASE_URL}/books`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    title, 
                    author, 
                    description, 
                    status 
                }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                await loadBooks();
                addBookForm.reset();
                document.querySelector('.tab[data-tab="myBooks"]').click();
            } else {
                throw new Error(data.error || 'Failed to add book');
            }
        } catch (error) {
            showError('addBook', error.message);
            console.error('Error adding book:', error);
        } finally {
            showLoading('addBook', false);
        }
    }

    async function loadProfile() {
        try {
            showLoading('profile', true);
            const response = await fetch(`${API_BASE_URL}/users/me`, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const user = await response.json();
                displayProfile(user);
            } else {
                throw new Error('Failed to load profile');
            }
        } catch (error) {
            console.error('Error loading profile:', error);
            showError('profile', error.message);
        } finally {
            showLoading('profile', false);
        }
    }

    function displayProfile(user) {
        if (!user) return;
        
        profileInfo.innerHTML = `
            <p><strong>Username:</strong> ${user.username}</p>
            <p><strong>Email:</strong> ${user.email}</p>
            <p><strong>Member since:</strong> ${new Date(user.created_at).toLocaleDateString()}</p>
        `;
        
        // Pre-fill the update form
        document.getElementById('updateUsername').value = user.username || '';
        document.getElementById('updateEmail').value = user.email || '';
    }

    async function handleUpdateProfile() {
        const username = document.getElementById('updateUsername').value;
        const email = document.getElementById('updateEmail').value;
        const password = document.getElementById('updatePassword').value;
        
        if (!username && !email && !password) {
            showError('updateProfile', 'No changes to update');
            return;
        }

        try {
            showLoading('updateProfile', true);
            const response = await fetch(`${API_BASE_URL}/users/me`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    username: username || undefined,
                    email: email || undefined,
                    password: password || undefined
                }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                await loadProfile();
                if (username) {
                    usernameDisplay.textContent = username;
                }
                alert('Profile updated successfully');
            } else {
                throw new Error(data.error || 'Failed to update profile');
            }
        } catch (error) {
            showError('updateProfile', error.message);
            console.error('Error updating profile:', error);
        } finally {
            showLoading('updateProfile', false);
            document.getElementById('updatePassword').value = '';
        }
    }

    function showLoading(context, isLoading) {
        const elements = {
            'login': {
                text: 'loginText',
                spinner: 'loginSpinner',
                button: 'loginSubmit'
            },
            'register': {
                text: 'registerText',
                spinner: 'registerSpinner',
                button: 'registerSubmit'
            },
            'addBook': {
                text: 'addBookText',
                spinner: 'addBookSpinner',
                button: 'addBookSubmit'
            },
            'updateProfile': {
                text: 'updateProfileText',
                spinner: 'updateProfileSpinner',
                button: 'updateProfileSubmit'
            },
            'logout': {
                button: 'logoutBtn'
            }
        };

        if (elements[context]) {
            const { text, spinner, button } = elements[context];
            
            if (text && spinner) {
                document.getElementById(text).classList.toggle('hidden', isLoading);
                document.getElementById(spinner).classList.toggle('hidden', !isLoading);
            }
            
            if (button) {
                document.getElementById(button).disabled = isLoading;
            }
        }
    }

    function showError(context, message) {
        const errorElements = {
            'login': 'loginError',
            'register': 'registerError',
            'addBook': 'addBookError',
            'updateProfile': 'updateProfileError',
            'books': 'bookList',
            'profile': 'profileInfo'
        };

        const elementId = errorElements[context];
        if (!elementId) return;

        const element = document.getElementById(elementId);
        if (element) {
            if (context === 'books' || context === 'profile') {
                element.innerHTML = `<p class="error-message">${message}</p>`;
            } else {
                element.textContent = message;
                element.classList.remove('hidden');
            }
        }
    }

    function hideError(context) {
        const elementId = errorElements[context];
        if (elementId) {
            const element = document.getElementById(elementId);
            if (element) {
                element.classList.add('hidden');
            }
        }
    }
});