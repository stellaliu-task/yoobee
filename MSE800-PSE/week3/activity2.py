class Student:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.scores = {}

    def add_score(self, subject, score):
        self.scores[subject] = score

    def return_score(self):
        print(f"These are results of ID: {self.student_id} {self.name}")
        print('-'*30)
        for subject, score in self.scores.items():
            print(f"subject:{subject}  {score}")
        print('-'*30)


class System:
    def __init__(self):
        self.student = {}
    
    def add_student(self,student_id, name ):
        self.student[student_id] = Student(student_id, name)
        print(f"Student {name} added")
        print('-'*30)


    def add_score(self, student_id, subject, score):
        self.student[student_id].add_score(subject, score)
        print(f"The scores of student {self.student[student_id].name} added")
        print('-'*30)

    def show_result(self):
        for student_id, name in self.student.items():
            #print(f"Student {name}'s scores: ")
            #print('*'*30)
            print('\n')
            self.student[student_id].return_score()
            print('*'*30)

def main():
    system = System()
    system.add_student(10001,'Fiona Davis')
    system.add_student(10002,'Carter Wilson')
    system.add_student(10003,'Becca Day')

    system.add_score(10001, 'English', 76)
    system.add_score(10001, 'Math', 87)
    system.add_score(10001, 'Science', 90)

    system.add_score(10002, 'English', 89)
    system.add_score(10002, 'Math', 88)
    system.add_score(10002, 'Science', 93)

    system.add_score(10003, 'English', 80)
    system.add_score(10003, 'Math', 75)
    system.add_score(10003, 'Science', 83)

    system.show_result()

if __name__ == "__main__":
    main()
