from database import create_table
from user_manager import add_user, view_users, search_user, delete_user, advanced_search
from course_manager import add_course, view_courses, search_course

def menu():
    print("\n==== User Manager ====")
    print("1. Add User")
    print("2. View All Users")
    print("3. Search User by Name")
    print("4. Delete User by ID")
    print("5. Search User by ID and Name")
    print("0. Exit")
   # print("6. Add course")
    print("7. View All courses")
    print("8. Add course")
    print("9. Search score by Course ID and Student Name")

def main():
    create_table()
    while True:
        menu()
        choice = input("Select an option (0-9): ")
        if choice == '1':
            name = input("Enter name: ")
            email = input("Enter email: ")
            add_user(name, email)
        elif choice == '2':
            users = view_users()
            for user in users:
                print(user)
            break
        elif choice == '3':
            name = input("Enter name to search: ")
            users = search_user(name)
            for user in users:
                print(user)
        elif choice == '4':
            user_id = int(input("Enter user ID to delete: "))
            delete_user(user_id)
        elif choice == '0':
            print("Goodbye!")
            break
        elif choice == '5':
            name = input("Enter name to search: ")
            user_id = input("Enter id to search: ")
            users = advanced_search(user_id, name)
            if results:
                for user in users:
                    print(user)
            else:
                print("No matching user or course found.")        
            break   
        elif choice == '7':
            courses = view_courses()
            for name in courses:
                print(courses)
        if choice == '8':
            name = input("Enter course name: ")
            unit = input("Enter course unit: ")
            student_id = input("Enter student id:")
            score = input("Enter score: ")
            add_course(name, unit, student_id, score) 
        elif choice == '9':
            id = input("Enter course id to search:")
            student_name = input("Enter student name to search: ")
            results = search_course(id, student_name)
            if results:
                for row in results:
                    print(f"User: {row[0]}, Course: {row[1]}, Score: {row[2]}")
            else:
                print("No matching user or course found.")        
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()
