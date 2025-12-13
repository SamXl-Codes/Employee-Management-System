# Working with Database 

from tkinter import *
from tkinter import ttk
import sqlite3

try:
    con = sqlite3.connect('student_data.sqlite3')          # Connecting to SQLite DB
except sqlite3.DatabaseError:
    print("Can not connect with the database sqlite3")

cur = con.cursor()                                           # Creating a cursor
cur.execute('drop table if exists StudentData')
cur.execute('CREATE TABLE StudentData (StudId NUMBER, StudName TEXT, Course TEXT)')
print("Table is created....")

root = Tk()
root.geometry('400x600')

frm1 = ttk.Frame(root)
frm1.grid(row=0,column=0)

l1 = Label(frm1, text="Student ID ")
e1 = Entry(frm1, width=20)
l1.grid(row=1, column=0)
e1.grid(row=1, column=1)

l2 = Label(frm1, text="Student Name ")
e2 = Entry(frm1, width=20)
l2.grid(row=2, column=0)
e2.grid(row=2, column=1)

l3 = Label(frm1, text="Course  ")
e3 = Entry(frm1, width=20)
l3.grid(row=3, column=0)
e3.grid(row=3, column=1)

def show(arg1, arg2, arg3):
    print(arg1, "\n",arg2, "\n",arg3)
    clear_text()
    insert_record(arg1, arg2, arg3)

def insert_record(arg1, arg2, arg3):
    try:
        print(arg1, "\n",arg2, "\n",arg3)
        str = "INSERT INTO StudentData VALUES("+arg1+"," + "'"+ arg2 + "'" + "," + "'"+ arg3 + "'"+")"
        print(str)
        cur.execute(str)
        print("Record is inserted.....")
    
        con.commit()
        
        print("Data is saved.....")
        
        cur.execute("SELECT * FROM StudentData")        # Display all records in terminal window
        for row in cur:
            print(row)
                
    except sqlite3.DatabaseError:
        print("Error ")
        con.rollback()
 
def clear_text():
    e1.delete(0, END)
    e2.delete(0, END)
    e3.delete(0, END)
        
# lambda is anonymous function/expression, it can accept any number of arguments but can have only one expression, allows to send multiple data through the function
# here in button command it is used to pass data to a callback function 

btn_show = Button(frm1, text="Add Record ", command=lambda: show(e1.get(), e2.get(), e3.get()))
btn_show.grid(row=4,column=0)

btn_clear = Button(frm1, text="Clear", command=lambda: clear_text())
btn_clear.grid(row=4, column=1) 

btn_exit = Button(frm1,text="Exit", command=root.destroy).grid(row=4, column=2)

root.mainloop()

