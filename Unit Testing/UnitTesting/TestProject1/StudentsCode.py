# definition of class Student

class Student:
    def __init__(self, fname, lname, stud_id,year):
        self.fname = fname
        self.lname = lname 
        self.stud_id = stud_id
        self.year = year
        self.grad_year = 0
    
    @property
    def email(self):
        email = self.fname+"."+self.lname+"@dbs.ie"
        return(email)
    
    @property
    def full_name(self):
        full_name = self.fname+" "+self.lname
        return(full_name)
    
    def getGraduationYear(self):
        self.grad_year = self.year + 1
        return(self.grad_year)
"""
class MainClass:
    s1 = Student("Swati","Dongre",5001111,2024)
    print("Student Name: ",s1.full_name)
    print("Student Email: ", s1.email)
    print("Year of Graduation: ",s1.getGraduationYear())
"""    