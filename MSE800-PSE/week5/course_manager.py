from database import create_connection
import sqlite3

def add_course(name, unit, student_id, score):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO courses (name, unit, student_id, score) VALUES (?, ?, ?, ?)", (name, unit, student_id, score))
    conn.commit()
    print(" Course added successfully.")
    conn.close()

def view_courses():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses")
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_course(course_id,student_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT users.name, courses.name, courses.score
        FROM users
        JOIN courses ON users.id = courses.student_id
        WHERE courses.id = ? AND users.name = ?
    ''', (course_id, student_name))
    rows = cursor.fetchall()
    conn.close()
    return rows