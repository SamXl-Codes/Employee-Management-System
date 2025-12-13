#unittest - working with unittest 
import unittest
from StudentClass import Student

class testStudent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s1 = Student( "Samuel", "Ogunlusi", 20086108, 2025)
        cls.s2 = Student( "Jane", "Doe", 200012345, 2024)
        return super().setUpClass()
    @classmethod
    def tearDownClass(cls):
        print ("Release the resources...")

    def test1_email(self):
        self.assertEqual(self.s1.email, "samuel.ogunlusi@dbs.ie")

    def test2_fullname(self):
        self.assertEqual(self.s1.fullname, "Samuel Ogunlusi")

    #Unittest to test method getGraduationYear
    def test3_getGraduationYear(self):
        self.assertEqual(self.s1.getGraduationYear(), 2026) 

if __name__ == '__main__':
    unittest.main() 