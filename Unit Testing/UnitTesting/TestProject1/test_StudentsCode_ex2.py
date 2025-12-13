# unit tests to test class Student 
# Use of classmethods setUpClass() and tearDownClass()

import unittest
from StudentsCode import Student

class testStudents(unittest.TestCase):
    @classmethod                                                # Must be decorated as class method 
    def setUpClass(cls):                                        # setUpClass() class method is called before the tests (in an individual class) are run. It has class as the only argument
        cls.s1 = Student("Joel","Patrick",20012222,2023)
        cls.s2 = Student("Sheefa","Shah",20013333, 2025)
        return super().setUpClass()
    
    @classmethod                                                # Must be decorated as class method
    def tearDownClass(cls):                                     # tearDownClass() class method is called after all tests (in an individual class) have run. It has class as the only argument
        print("\n\nTear down a class")
        print("Releasing the resources")
        return super().tearDownClass()
    
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