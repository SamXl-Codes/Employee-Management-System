# unittest - working with unit testing framework
# unit tests to test class Student 

# test runner- A test runner is a component which orchestrates the execution of tests and 
# provides the outcome to the user. The runner may use a graphical interface, a textual interface, 
# or return a special value to indicate the results of executing the tests.

# tests should be isolated 

import unittest
from StudentsCode import Student

class testStudents(unittest.TestCase):                  # unittest provides a base class, TestCase, which may be used to create new test cases.
    
    def test1_email(self):
        s1 = Student("Joel","Patrick",20012222,2023)
        #self.assertEqual(s1.email,"joel.patrick@dbs.ie")
        self.assertEqual(s1.email,"Joel.Patrick@dbs.ie")
    
    def test2_full_name(self):
        s2 = Student("Sheefa","Shah",20013333, 2025)
        self.assertEqual(s2.full_name,"Sheefa Shah")
        
    
if __name__ == "__main__":
    unittest.main()