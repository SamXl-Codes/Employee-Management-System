# GUI -3 
# Use of widgets: Entry, Label, Button 
# Display contents on UI and console 

from tkinter import *
from tkinter import ttk

root = Tk()
root.geometry('400x600')
root.title('Working with entry boxes ')

frm1 = ttk.Frame(root)
frm1.grid(row=0,column=0)

l1 = Label(frm1, text="User Name ")
e1 = Entry(frm1, width=20)
l1.grid(row=1, column=0)
e1.grid(row=1, column=1)

l1 = Label(frm1,text="")

def show(args):
    l1.config(text=args)
    l1.grid(row=5, column=1)
    print(args)
    clear_text()

def clear_text():
    e1.delete(0, END)
        
# lambda is anonymous function/expression, 
# here in button command it is used to pass data to a callback function 

btn_show = Button(frm1, text="Show ", command=lambda: show(e1.get()))
btn_show.grid(row=2,column=0)

btn_clear = Button(frm1, text="Clear", command=lambda: clear_text())
btn_clear.grid(row=2, column=1) 

btn_exit = Button(frm1,text="Exit", command=root.destroy).grid(row=2, column=2)
root.mainloop()

# Write a code to display a message "Download button clicked", when a "Download" button is clicked
