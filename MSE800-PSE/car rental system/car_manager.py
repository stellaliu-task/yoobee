import sqlite3


class CarManager:
    def __init__(self, conn):
        self.conn = conn

    def _execute_query(self, query, params=()):
        """Helper method to execute queries with error handling"""
        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            return cur
        except sqlite3.Error as e:
            raise ValueError(f"Database error: {str(e)}")

    def add_car(self, car_data, image_file=None):
        """Add a new car to the database"""
        query = '''INSERT INTO cars(
            name, picture, fuel_type, gear_type, 
            seats, location, price, insurance_price
            ) VALUES(?,?,?,?,?,?,?,?)'''
        
        image_data = image_file.read() if image_file else None
        params = (
            car_data.get('name'),
            image_data,
            car_data.get('fuel_type'),
            car_data.get('gear_type'),
            car_data.get('seats'),
            car_data.get('location'),
            car_data.get('price'),
            car_data.get('insurance_price')
        )
        
        cur = self._execute_query(query, params)
        self.conn.commit()
        return cur.lastrowid

    def search_available_cars(self, start_datetime, end_datetime, location=None):
        """Search for available cars within a date range"""
        query = '''SELECT id, name, fuel_type, gear_type, seats, location,
                   price, insurance_price FROM cars 
                   WHERE id NOT IN (
                       SELECT car_id FROM orders 
                       WHERE ? < end_datetime AND ? > start_datetime
                   )'''
        params = [
            end_datetime.replace('T', ' ') if isinstance(end_datetime, str) else end_datetime,
            start_datetime.replace('T', ' ') if isinstance(start_datetime, str) else start_datetime
        ]
        
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        
        cur = self._execute_query(query, params)
        cars = [dict(zip([col[0] for col in cur.description], row)) for row in cur.fetchall()]
        
        for car in cars:
            car['image_url'] = f"/api/cars/{car['id']}/image"
        return cars

    def get_car_image(self, car_id):
        """Get car image by car ID"""
        cur = self._execute_query("SELECT picture FROM cars WHERE id = ?", (car_id,))
        result = cur.fetchone()
        return result[0] if result else None

    def get_all_cars(self):
        """Get all cars with proper error handling"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT id, name, fuel_type, gear_type, 
                    seats, location, price, insurance_price
                FROM cars
            """)
            
            columns = [col[0] for col in cur.description]
            cars = []
            
            for row in cur.fetchall():
                car = dict(zip(columns, row))
                car['image_url'] = f"/api/cars/{car['id']}/image"
                cars.append(car)
                
            return cars
            
        except sqlite3.Error as e:
            print(f"Database error in get_all_cars: {str(e)}")
            raise ValueError("Failed to retrieve cars")
        except Exception as e:
            print(f"Unexpected error in get_all_cars: {str(e)}")
            raise
    def get_car_by_id(self, car_id):
        """Get a single car by ID without the binary image data"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT id, name, fuel_type, gear_type, seats, 
                    location, price, insurance_price
                FROM cars 
                WHERE id = ?
            """, (car_id,))
            
            result = cur.fetchone()
            if result:
                columns = [col[0] for col in cur.description]
                return dict(zip(columns, result))
            return None
        except sqlite3.Error as e:
            raise ValueError(f"Database error: {str(e)}")
    
    def update_car(self, car_id, data, image_file=None):
        """Update car information"""
        allowed_fields = {
            'name', 'fuel_type', 'gear_type', 'seats', 
            'location', 'price', 'insurance_price'
        }
        
        updates = []
        params = []
        
        for field, value in data.items():
            if field in allowed_fields and value is not None:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if image_file:
            updates.append("picture = ?")
            params.append(image_file.read())
        
        if not updates:
            return False
        
        query = f"UPDATE cars SET {', '.join(updates)} WHERE id = ?"
        params.append(car_id)
        
        cur = self._execute_query(query, params)
        self.conn.commit()
        return cur.rowcount > 0