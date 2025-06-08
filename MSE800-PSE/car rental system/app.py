from flask import Flask, request,session,jsonify, render_template, send_from_directory, g, make_response,redirect
from database import Database
from user_manager import UserManager
import os
from order_manager import OrderManager
from car_manager import CarManager
from admin_manager import AdminManager
from datetime import datetime
from functools import wraps
import base64


app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = '^GKIOJFHIJPK"K::JL12'

def get_db():
    if 'db' not in g:
        g.db = Database()
    return g.db

def get_user_manager():
    if 'user_manager' not in g:
        g.user_manager = UserManager(get_db().conn)
    return g.user_manager

def get_admin_manager():
    if 'admin_manager' not in g:
        g.admin_manager = AdminManager(get_db().conn)
    return g.admin_manager
"""
@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
"""
@app.after_request
def add_no_cache_headers(response):
    """Add headers to prevent caching"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
def index():
    return render_template('index.html')
#def home():
#    return render_template('dashboard.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/login', methods=['POST'])
def login():
    user_manager = get_user_manager()
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = user_manager.login(email, password)
    if user:
        session['user_id'] = user['id']  # Store user ID in session
        session.permanent = True  # Make session persistent
        return jsonify({'user': user})
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    user_manager = get_user_manager()  # Get the UserManager instance
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    try:
        user_id = user_manager.signup(email, password)
        user = user_manager.get_user_profile(user_id)
        return jsonify({'user_id': user_id, 'user': user})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/dashboard')
@app.route('/dashboard.html') 
def dashboard():
    return render_template('dashboard.html')

def get_order_manager():
    if 'order_manager' not in g:
        g.order_manager = OrderManager(get_db().conn)
    return g.order_manager

@app.route('/search')
def search_page():
    return render_template('search.html')
'''
@app.route('/api/cars/available', methods=['GET'])
def get_available_cars():
    car_manager = get_car_manager()
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        location = request.args.get('location')
        
        if not start or not end:
            return jsonify({'error': 'Start and end dates are required'}), 400
            
        cars = car_manager.search_available_cars(start, end, location)
        return jsonify([dict(car) for car in cars])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
'''
@app.route('/api/orders', methods=['POST'])
def create_order():
    order_manager = get_order_manager()
    try:
        data = request.get_json()
        order_id = order_manager.create_order(data)
        return jsonify({'order_id': order_id})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

def get_car_manager():
    if 'car_manager' not in g:
        g.car_manager = CarManager(get_db().conn)
    return g.car_manager

@app.route('/api/cars/<int:car_id>/image')
def get_car_image(car_id):
    try:
        car_manager = get_car_manager()
        image_data = car_manager.get_car_image(car_id)
        
        if not image_data:
            # Serve default aqua.jpeg if no image exists
            default_image_path = os.path.join(app.static_folder, 'pics', 'aqua.jpeg')
            if os.path.exists(default_image_path):
                with open(default_image_path, 'rb') as f:
                    image_data = f.read()
            else:
                return jsonify({'error': 'Image not found'}), 404
            
        response = make_response(image_data)
        response.headers.set('Content-Type', 'image/jpeg')
        return response
        
    except Exception as e:
        print(f"Error getting car image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cars/available', methods=['GET'])
def get_available_cars():
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        
        if not start or not end:
            return jsonify({
                'error': 'Both start and end parameters are required',
                'example': '/api/cars/available?start=2025-01-01T10:00&end=2025-01-05T10:00'
            }), 400

        location = request.args.get('location')
        car_manager = get_car_manager()
        
        cars = car_manager.search_available_cars(start, end, location)
        return jsonify(cars)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error in /api/cars/available: {str(e)}")
        return jsonify({'error': 'Failed to search for available cars'}), 500

@app.teardown_appcontext
def teardown_db(exception):
    # Clean up database connection and managers
    db = g.pop('db', None)
    if db is not None:
        db.close()
    
    # Clean up all manager instances
    for manager in ['car_manager', 'order_manager', 'user_manager']:
        if manager in g:
            g.pop(manager)

@app.route('/order')
def order_page():
    return render_template('order.html')

@app.route('/api/orders/<int:order_id>')
def get_order_details(order_id):
    try:
        order_manager = get_order_manager()
        cur = order_manager.conn.cursor()
        
        # Get order with car details
        cur.execute('''
            SELECT o.*, c.name as car_name, c.fuel_type, c.gear_type, c.seats, 
                   c.location, c.price, c.insurance_price
            FROM orders o
            JOIN cars c ON o.car_id = c.id
            WHERE o.id = ?
        ''', (order_id,))
        
        order = cur.fetchone()
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Convert to dict
        columns = [col[0] for col in cur.description]
        order_dict = dict(zip(columns, order))
        
        # Format the response
        return jsonify({
            'id': order_dict['id'],
            'start_datetime': order_dict['start_datetime'],
            'end_datetime': order_dict['end_datetime'],
            'created_at': order_dict['created_at'],  # Using start time as created for demo
            'car': {
                'id': order_dict['car_id'],
                'name': order_dict['car_name'],
                'fuel_type': order_dict['fuel_type'],
                'gear_type': order_dict['gear_type'],
                'seats': order_dict['seats'],
                'location': order_dict['location'],
                'price': order_dict['price'],
                'insurance_price': order_dict['insurance_price']
            }
        })
        
    except Exception as e:
        print(f"Error getting order details: {str(e)}")
        return jsonify({'error': str(e)}), 500
@app.route('/user')
def user_page():
    return render_template('user.html')

@app.route('/api/user')
def api_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_manager = get_user_manager()
    user = user_manager.get_user_profile(session['user_id'])

    print("DEBUG USER PROFILE:", user)

    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or 'Not provided',
        'email': user.get('email', 'Not provided'),
        'phone': user.get('phone_number', 'Not provided'),
        'card_number': user.get('card_number', 'Not provided'),
        'driver_licence_number': user.get('driver_licence_number', 'Not provided'),
        'driver_licence_country': user.get('driver_licence_country', 'Not provided'),
        'licence_expiry_date': user.get('licence_expiry_date', 'Not provided')
    })

@app.route('/api/user/orders')
def api_user_orders():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    order_manager = get_order_manager()
    try:
        orders = order_manager.get_user_orders(session['user_id'])
        
        formatted_orders = []
        for order in orders:
            order_dict = dict(order)
            try:
                # Handle datetime parsing with multiple formats
                def parse_dt(dt_str):
                    if not dt_str:
                        return None
                    # Remove timezone if present
                    dt_str = dt_str.split('+')[0].split('.')[0]
                    # Try with T separator first, then space
                    for sep in ['T', ' ']:
                        for fmt in [f'%Y-%m-%d{sep}%H:%M:%S', f'%Y-%m-%d{sep}%H:%M']:
                            try:
                                return datetime.strptime(dt_str, fmt)
                            except ValueError:
                                continue
                    return None
                
                start_dt = parse_dt(order_dict['start_datetime'])
                end_dt = parse_dt(order_dict['end_datetime'])
                created_dt = parse_dt(order_dict.get('created_at')) or start_dt
                
                if not start_dt or not end_dt:
                    raise ValueError("Invalid date format")
                
                # Calculate duration and price
                days = max(1, (end_dt - start_dt).days)  # Ensure at least 1 day
                total_price = (order_dict['price'] * days) + (order_dict['insurance_price'] * days)
                
                formatted_orders.append({
                    'id': order_dict['id'],
                    'car_name': order_dict['car_name'],
                    'start_datetime': start_dt.isoformat(),
                    'end_datetime': end_dt.isoformat(),
                    'total_price': round(total_price, 2),
                    'created_at': created_dt.isoformat() if created_dt else None,
                    'raw_data': order_dict  # For debugging
                })
                
            except Exception as e:
                print(f"Error formatting order {order_dict.get('id')}: {str(e)}")
                # Fallback with raw values
                formatted_orders.append({
                    'id': order_dict['id'],
                    'car_name': order_dict['car_name'],
                    'start_datetime': order_dict['start_datetime'],
                    'end_datetime': order_dict['end_datetime'],
                    'total_price': round(order_dict.get('price', 0), 2),
                    'created_at': order_dict.get('created_at', order_dict.get('start_datetime')),
                    'raw_data': order_dict,
                    'error': str(e)
                })
        
        # Sort orders by created_at descending (newest first)
        formatted_orders.sort(key=lambda x: (
            x.get('created_at') or x.get('start_datetime') or ''
        ), reverse=True)
        
        return jsonify(formatted_orders)
        
    except Exception as e:
        print(f"Error in api_user_orders: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-session')
def check_session():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({'status': 'active'})

@app.route('/api/cars/all', methods=['GET'])
def get_all_cars():
    car_manager = get_car_manager()
    try:
        cars = car_manager.get_all_cars()
        return jsonify([dict(car) for car in cars])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/user-info')
def user_info_page():
    return render_template('user-info.html')

@app.route('/user-orders')
def user_orders_page():
    return render_template('user-orders.html')

@app.route('/edit-profile')
def edit_profile_page():
    return render_template('edit-profile.html')

@app.route('/api/user/update', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_manager = get_user_manager()
    data = request.get_json()
    
    try:
        success = user_manager.update_profile(session['user_id'], data)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'No valid fields to update'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/admin')
@app.route('/admin/cars')
def admin_cars_page():
    if 'admin_id' not in session:
        return redirect('/admin-login')
    return render_template('admin-cars.html')

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin-login')
def admin_login_page():
    """Render the admin login page"""
    return render_template('admin-home.html')

@app.route('/admin-home')
def admin_home():
    return render_template('admin-home.html')

# Admin login route
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    print("LOGIN attempt data:", data)  # print received data

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    admin_manager = get_admin_manager() 
    cur = get_db().conn.cursor()
    cur.execute("SELECT * FROM admin WHERE email=?", (email,))
    admin = cur.fetchone()
    print("DB lookup for admin:", admin)

    if admin and admin_manager._verify_password(admin['password_hash'], password):
        session['admin_id'] = admin['id']
        return jsonify({'success': True})
    
    print("Password check failed.")
    return jsonify({'error': 'Invalid credentials'}), 401

# Admin car management routes
@app.route('/api/admin/cars', methods=['GET'])
@admin_required
def get_all_cars_admin():
    try:
        car_manager = get_car_manager()
        cars = car_manager.get_all_cars()
        
        # Convert each car to a dictionary and handle image URLs
        car_list = []
        for car in cars:
            car_dict = dict(car)
            car_dict['image_url'] = f"/api/cars/{car_dict['id']}/image"
            car_list.append(car_dict)
            
        return jsonify(car_list)
        
    except Exception as e:
        print(f"Error fetching cars: {str(e)}")  
        return jsonify({'error': 'Failed to fetch cars', 'details': str(e)}), 500

@app.route('/api/admin/cars/<int:car_id>', methods=['PUT'])
@admin_required
def update_car(car_id):
    try:
        data = request.form.to_dict()
        image_file = request.files.get('image')
        
        car_manager = get_car_manager()
        car_manager.update_car(car_id, data, image_file)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/create-admin')
def create_admin():
    email = "admin@premiumrentals.com"
    password = "securepassword123"
    
    user_manager = get_user_manager()
    hashed_pw = user_manager._hash_password(password)
    
    cur = get_db().conn.cursor()
    cur.execute("INSERT INTO admin (name, email, password_hash) VALUES (?, ?, ?)",
              ("System Admin", email, hashed_pw))
    get_db().conn.commit()
    
    return "Admin created"

@app.route('/api/locations')
def get_locations():
    cur = get_db().conn.cursor()

    rows = cur.execute("SELECT DISTINCT location FROM cars WHERE location IS NOT NULL AND location != ''").fetchall()
    locations = sorted([row['location'] for row in rows if row['location']])
    return jsonify(locations)

# Get a single car by id (for editing)
@app.route('/api/admin/cars/<int:car_id>')
def api_admin_get_car(car_id):
    cur = get_db().conn.cursor()
    cur.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({'error': 'Car not found'}), 404

    columns = [desc[0] for desc in cur.description]
    car = dict(zip(columns, row))

    if car.get('picture'):
        car['image_base64'] = base64.b64encode(car['picture']).decode('utf-8')
        del car['picture']  # Remove the raw BLOB

    return jsonify(car)


# Update car details
@app.route('/api/admin/cars/<int:car_id>', methods=['PUT'])
def api_admin_update_car(car_id):
    data = request.get_json()
    cur = get_db().conn.cursor()
    cur.execute("""
        UPDATE cars
        SET name=?, location=?, price=?, seats=?, fuel_type=?, gear_type=?, image_url=?
        WHERE id=?
    """, (
        data['name'], data['location'], data['price'], data['seats'],
        data['fuel_type'], data['gear_type'], data['image_url'], car_id
    ))
    get_db().conn.commit()
    return jsonify({'message': 'Car updated'})

@app.route('/admin/cars/edit/<int:car_id>')
def admin_edit_car_page(car_id):
    return render_template('admin-edit-car.html')

@app.route('/api/admin/orders')
def api_admin_orders():
    conn = get_db().conn 
    orders = AdminManager.get_all_orders(conn)
    formatted_orders = []
    for row in orders:
        order_dict = dict(row)
        try:
            # Parse datetimes
            from datetime import datetime
            def parse_dt(dt_str):
                if not dt_str:
                    return None
                dt_str = dt_str.split('+')[0].split('.')[0]
                for sep in ['T', ' ']:
                    for fmt in [f'%Y-%m-%d{sep}%H:%M:%S', f'%Y-%m-%d{sep}%H:%M']:
                        try:
                            return datetime.strptime(dt_str, fmt)
                        except ValueError:
                            continue
                return None
            start_dt = parse_dt(order_dict['start_datetime'])
            end_dt = parse_dt(order_dict['end_datetime'])
            created_dt = parse_dt(order_dict.get('created_at')) or start_dt

            days = max(1, (end_dt - start_dt).days) if start_dt and end_dt else 1
            price = float(order_dict.get('price', 0) or 0)
            insurance = float(order_dict.get('insurance_price', 0) or 0)
            total_price = (price * days) + (insurance * days)

            order_dict['total_price'] = round(total_price, 2)
            order_dict['start_datetime'] = start_dt.isoformat() if start_dt else order_dict.get('start_datetime')
            order_dict['end_datetime'] = end_dt.isoformat() if end_dt else order_dict.get('end_datetime')
            order_dict['created_at'] = created_dt.isoformat() if created_dt else order_dict.get('created_at')
            formatted_orders.append(order_dict)
        except Exception as e:
            print(f"Error formatting order {order_dict.get('id')}: {str(e)}")
            order_dict['total_price'] = 0
            formatted_orders.append(order_dict)
    return jsonify(formatted_orders)

@app.route('/api/admin/orders/<int:order_id>/returned', methods=['POST'])
def api_admin_order_returned(order_id):
    conn = get_db().conn
    cur = conn.cursor()
    cur.execute("UPDATE orders SET returned = 1 WHERE id = ?", (order_id,))
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/user/review')
def api_user_get_review():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    order_id = request.args.get('order_id')
    if not order_id:
        return jsonify({'error': 'No order_id'}), 400
    conn = get_db().conn
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM reviews
        WHERE user_id = ? AND car_id = (
            SELECT car_id FROM orders WHERE id = ?
        )
        AND EXISTS (
            SELECT 1 FROM orders WHERE id = ? AND user_id = ? AND returned = 1
        )
    ''', (session['user_id'], order_id, order_id, session['user_id']))
    review = cur.fetchone()
    if not review:
        return jsonify({'review': None})
    review = dict(review)
    return jsonify({'review': review})

@app.route('/api/user/review', methods=['POST'])
def api_user_post_review():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    user_id = session['user_id']
    order_id = request.form.get('order_id')
    ranking = request.form.get('ranking')
    review_content = request.form.get('review_content')
    if not all([order_id, ranking, review_content]):
        return jsonify({'error': 'Missing fields'}), 400
    conn = get_db().conn
    cur = conn.cursor()
    # Only allow review if order is returned
    cur.execute('SELECT car_id, returned FROM orders WHERE id = ? AND user_id = ?', (order_id, user_id))
    order = cur.fetchone()
    if not order or not order['returned']:
        return jsonify({'error': 'You cannot review this order'}), 403
    car_id = order['car_id']
    # Check if review already exists
    cur.execute('SELECT 1 FROM reviews WHERE user_id = ? AND car_id = ?', (user_id, car_id))
    if cur.fetchone():
        return jsonify({'error': 'You have already reviewed this car for this order'}), 400
    # Insert review
    cur.execute('''
        INSERT INTO reviews (submit_datetime, user_id, car_id, ranking, review_content, show_state)
        VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?, 1)
    ''', (user_id, car_id, ranking, review_content))
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/user/order/<int:order_id>')
def api_user_order(order_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    conn = get_db().conn
    cur = conn.cursor()
    cur.execute('''
        SELECT o.id, o.car_id, c.name as car_name, o.start_datetime, o.end_datetime
        FROM orders o
        JOIN cars c ON o.car_id = c.id
        WHERE o.id = ? AND o.user_id = ?
    ''', (order_id, session['user_id']))
    row = cur.fetchone()
    if not row:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(dict(row))

@app.route('/review')
def user_review_page():
    return render_template('user-review.html')

@app.route('/api/admin/reviews')
def api_admin_reviews():
    conn = get_db().conn
    cur = conn.cursor()
    cur.execute('''
        SELECT r.*, u.email as user_email, c.name as car_name
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        JOIN cars c ON r.car_id = c.id
    ''')
    reviews = cur.fetchall()
    reviews = [dict(row) for row in reviews]
    return jsonify(reviews)

@app.route('/api/admin/reviews/<int:review_id>/visibility', methods=['PUT'])
def api_admin_toggle_review_visibility(review_id):
    conn = get_db().conn
    cur = conn.cursor()
    # Get current show_state
    cur.execute("SELECT show_state FROM reviews WHERE id = ?", (review_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({'error': 'Review not found'}), 404
    new_state = not bool(row['show_state'])
    cur.execute("UPDATE reviews SET show_state = ? WHERE id = ?", (int(new_state), review_id))
    conn.commit()
    return jsonify({'success': True, 'show_state': int(new_state)})

@app.route('/api/reviews')
def api_car_reviews():
    car_id = request.args.get('car_id')
    if not car_id:
        return jsonify({'error': 'No car_id'}), 400
    conn = get_db().conn
    cur = conn.cursor()
    cur.execute('''
        SELECT r.ranking, r.review_content, r.submit_datetime, u.email
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.car_id = ? AND r.show_state = 1
        ORDER BY r.submit_datetime DESC
    ''', (car_id,))
    reviews = [dict(row) for row in cur.fetchall()]
    return jsonify(reviews)

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True)