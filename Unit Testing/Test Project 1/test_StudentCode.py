#unittest - working with unittest framework 

import unittest
from StudentClass import Student 

class TestStudent(unittest.TestCase):     #class inherits class unittest.TestCase
    def test1_email(self):
        s1 = Student("Samuel","Ogunlusi",200086108,2025)
        self.assertEqual(s1.email, "Samuel.Ogunlusi@dbs.ie")
    
    def test2_fullname(self):
        s2 = Student("Jane","Doe",200012345,2024)
        self.assertEqual(s2.fullname, "Jane Doe")
    # Unit 
if __name__ == '__main__':
    unittest.main()

