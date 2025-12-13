# Employee class

import requests

class Employee:
    band1 = 5000            # Class variables , static in nature
    band2 = 4000
    band3 = 2000
    tax1 = 0.3
    tax2 = 0.2
    tax3 = 0.1
    taxh = 0.5
        
    def __init__(self,emp_name, emp_id, salary):
        self.emp_name = emp_name
        self.emp_id = emp_id
        self.salary = salary
        if (self.validate_salary):
            self.netPay = self.cal_NetPay()
        else:
            print("Invalid data")
            exit
            
    def validate_salary(self):
        if self.salary > 0:
            return True
        else:
            return False
        
    def cal_NetPay(self):
        self.netpay = 0
        try:
            if self.salary < Employee.band3:                # or check the salary between given limits
                self.taxAmount = self.salary * Employee.tax3
                self.netpay = self.salary - self.taxAmount
            
            elif self.salary < Employee.band2:
                self.taxAmount = self.salary * Employee.tax2
                self.netpay = self.salary - self.taxAmount  
                
            elif self.salary < Employee.band1:
                self.taxAmount = self.salary * Employee.tax1
                self.netpay = self.salary - self.taxAmount  
            else:
                self.taxAmount = self.salary * Employee.taxh
                self.netpay = self.salary - self.taxAmount  
                  
        except Exception as e:
            print(e)
        finally:
            return self.netpay
    
    def printSalarySlip(self):
        print("- - - - - - - - - - - - - - - - - - - - - - - -")
        print("Employee Name: ",self.emp_name)
        print("Employee Id: ",self.emp_id)
        print("Salary: ",self.salary)
        print("Tax: ",self.taxAmount)
        print("Net Pay: ",self.netpay)
        print("- - - - - - - - - - - - - - - - - - - - - - - -")
    
    # Example: mocking
    def monthly_schedule(self,month):
        response = requests.get(f'http://company.com/{self.emp_name}/{month}')
        if (response.ok):
            return response.text
        else:
            return 'Bad Response!'

def main():
    e1 = Employee("Sean Jordan","A1001",5200)
    e2 = Employee("Sharad Pilley","M2323",3200)
    e3 = Employee("Shirley Smith","H100",1000)
    
    e1.printSalarySlip()
    e2.printSalarySlip()
    e3.printSalarySlip()


if __name__ == "__main__":
    main()
    