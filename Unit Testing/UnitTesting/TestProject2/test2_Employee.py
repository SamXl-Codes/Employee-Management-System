# Test Fixture Examples: setUp(), tearDown()
  
import unittest
from EmployeeCode import Employee

class testEmployee(unittest.TestCase):
    @classmethod                                    # classmethods work with class rather than the instance of the class
    def setUpClass(cls):
        print("Setting up the class - setUpClass()")
        cls.e1 = Employee("Sean Jordan","A1001",5200)
        cls.e2 = Employee("Sharad Pilley","M2323",3200)
        cls.e3 = Employee("Shirley Smith","H100",1000)
    
    @classmethod
    def tearDownClass(cls) -> None:
        print("Tearing down the class - tearDownClass()")
        return super().tearDownClass()
         
    def setUp(self):
        print("\nSet Up Method ")
    
    def tearDown(self):
        print("Tear Down")
    
        # anthother use case for tearDown - if you have to function to create a file in
        # a dirctory 
        # or a DB, you can delete the newly created objects in tearDown so that you 
        # will have a clean slate for your next test 
        
    def test1_calNetPay(self):
        pay = self.e1.cal_NetPay()
        self.assertEqual(pay,2600.0)
        
    def test2_calNetPay(self):
        pay = self.e2.cal_NetPay()
        self.assertEqual(pay,2560.00)

    def test3_calNetPay(self):
        pay = self.e3.cal_NetPay()
        self.assertEqual(pay,900.00)
    
    def test_validateSalary(self):
        e3 = Employee("Shirley Smith","H100", -2000)
        flag = e3.validate_salary()
        self.assertFalse(flag)
        #self.assertTrue(flag)       # test fails
        
if __name__ == "__main__":
    unittest.main()