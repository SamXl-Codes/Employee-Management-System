# unit tests to test class Student 
# Use of test fixture 

import unittest
from StudentsCode import Student

class testStudents(unittest.TestCase):
    def setUp(self):                                            #  method called to prepare test fixture. It is called before every test case 
        print("Set up method ")
        self.s1 = Student("Joel","Patrick",20012222,2023)
        self.s2 = Student("Sheefa","Shah",20013333, 2025)
        
    def tearDown(self):                                             #  Method called immediately after the test method has been called and the result recorded. This is called even if the test method raised an exception,
        print("\n\nTear down method")
      
    def test1_email(self):
        #self.assertEqual(s1.email,"joel.patrick@dbs.ie")
        self.assertEqual(self.s1.email,"Joel.Patrick@dbs.ie")                       # assert* methods are provided by TestCase class
    
    def test2_full_name(self):
        self.assertEqual(self.s2.full_name,"Sheefa Shah")
        
    def test3_getGraduationYear(self):
        grad_year = self.s1.getGraduationYear()
        self.assertEqual(grad_year, 2024)

if __name__ == "__main__":
    unittest.main()