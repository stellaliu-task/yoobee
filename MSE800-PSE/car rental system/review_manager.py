class ReviewManager():   
    def __init__(self, conn):
        self.conn = conn

    def add_review(conn, review_data):
        # Verify user actually rented the car
        verification_sql = '''
        SELECT id FROM orders 
        WHERE user_id = ? AND car_id = ? AND end_datetime < ?
        '''
        cur = conn.cursor()
        cur.execute(verification_sql, (
            review_data['user_id'],
            review_data['car_id'],
            review_data['submit_datetime']
        ))
        if not cur.fetchone():
            raise ValueError("User hasn't rented this car or rental isn't complete")
        
        insert_sql = '''INSERT INTO reviews(
                        submit_datetime, user_id, car_id, 
                        ranking, review_content, show_state)
                    VALUES(?,?,?,?,?,?)'''
        cur.execute(insert_sql, (
            review_data['submit_datetime'],
            review_data['user_id'],
            review_data['car_id'],
            review_data['ranking'],
            review_data['review_content'],
            review_data.get('show_state', True)
        ))
        conn.commit()
        return cur.lastrowid

    def get_car_reviews(conn, car_id, only_visible=True):
        sql = '''SELECT r.*, u.first_name, u.last_name 
                FROM reviews r JOIN users u ON r.user_id = u.id
                WHERE r.car_id = ?'''
        params = [car_id]
        
        if only_visible:
            sql += " AND r.show_state = TRUE"
            
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()