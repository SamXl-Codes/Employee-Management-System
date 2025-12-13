class Student:
    def __init__(self, first_name, last_name, student_id, year):
        assert isinstance(year, int), "Year must be an integer"
        self.first_name = first_name
        self.last_name = last_name
        self.student_id = student_id
        self.year = year
    
    @property
    def email(self):
        return f"{self.first_name.lower()}.{self.last_name.lower()}@dbs.ie"
    
    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"
    
    def getGraduationYear(self):
        return self.year + 1
