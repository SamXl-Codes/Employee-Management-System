#unittest - working with unittest 
import unittest
from StudentClass import Student

class testStudent(unittest.TestCase):
    def setUp(self):
        print ("SETUP METHOD")
        self.s1 = Student("Samuel", "Ogunlusi", 20086108, 2025)

    def tearDown(self):
        print("TEAR DOWN METHOD")

    def test_email(self):
        self.assertEqual(self.s1.email, "samuel.ogunlusi@dbs.ie")

    def test2_fullname(self):
        self.assertEqual(self.s1.fullname, "Samuel Ogunlusi")

    #Unittest to test method getGraduationYear
    def test3_getGraduationYear(self):
        self.assertEqual(self.s1.getGraduationYear(), 2026) 

if __name__ == '__main__':
    unittest.main() 