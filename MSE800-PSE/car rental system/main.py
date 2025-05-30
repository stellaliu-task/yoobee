from database import Database
from user_manager import UserManager
from car_manager import CarManager
from order_manager import OrderManager
import sqlite3
import os

def main():
    # Initialize database and managers
    db = Database()
    
    try:
        user_manager = UserManager(db.conn)
        car_manager = CarManager(db.conn)
        order_manager = OrderManager(db.conn)

        # Create a test user
        user_id = user_manager.signup("test0@example.com", "passwordtest123")
        print(f"Created user with ID: {user_id}")

        # Add a test car
        car_data = {
            'name': 'Test Car',
            'picture': 'toyota_corolla.jpg',
            'fuel_type': 'gas',
            'gear_type': 'automatic',
            'seats': 4,
            'location': 'Auckland city',
            'available_datetime': '2025-06-23 09:00:00',
            'price': 89.99,
            'insurance_price': 15.00
        }
        car_manager.add_car(car_data)

        # Search for available cars
        available_cars = car_manager.search_available_cars(
            '2025-08-01 10:00', 
            '2025-08-05 10:00',
            location='Auckland airport'
        )
        print(f"Found {len(available_cars)} available cars")

        if available_cars:
            order_id = order_manager.create_order({
                'start_datetime': '2025-08-01 10:00',
                'end_datetime': '2025-08-05 10:00',
                'user_id': user_id,
                'car_id': available_cars[0]['id']
            })
            print(f"Created order with ID: {order_id}")

    except Exception as e:
        print(f"Error in main(): {e}")
    finally:
        db.close()

def update_all_car_images():
    try:
        # Connect to the database
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()
        
        # Get the absolute path to the image
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, 'static', 'pics', 'aqua.jpeg')
        
        # Verify the image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at: {image_path}")
        
        # Read the image file
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Update all cars in the database
        cursor.execute('UPDATE cars SET picture = ?', (image_data,))
        
        # Commit changes and close connection
        conn.commit()
        print(f"Successfully updated {cursor.rowcount} cars with aqua.jpeg image")
        
    except Exception as e:
        print(f"Error in update_all_car_images(): {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
    
    # Then update the car images
    update_all_car_images()