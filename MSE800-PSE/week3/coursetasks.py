class Camera:
    def __init__(self, date):
        self.date = date

    def capture(self):
      print('get students images')
        
    def process(self):
      print('saved images')

class Student:
    def __init__(self, student_id):
       self.student_id = student_id

    def indentify(self, student_id):
        print('student indentified')

    def show_results(self,student_id):
        print('student attended class')

class Checknumber:
    def __init__(self,num):
        self.num = num

    def check(self):
        if self.num <= 1:
            return False
        else:
            for i in range(2,self.num):
                if(self.num % i) == 0:
                    return False
                    break
                else:
                    return True
                
checknumber = Checknumber(5)
print(checknumber.check())
