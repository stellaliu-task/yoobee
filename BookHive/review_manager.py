class ReviewManager():   
    def __init__(self, conn):
        self.conn = conn

    def add_review(self, review_data):
        cur = self.cursor()
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
        self.commit()
        return cur.lastrowid

    def get_reviews(self, car_id, only_visible=True):
        sql = '''SELECT r.*, u.first_name, u.last_name 
                FROM reviews r JOIN users u ON r.user_id = u.id
                WHERE r.car_id = ?'''
        params = [car_id]
        
        if only_visible:
            sql += " AND r.show_state = TRUE"
            
        cur = self.cursor()
        cur.execute(sql, params)
        return cur.fetchall()