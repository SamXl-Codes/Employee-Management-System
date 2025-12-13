# GUI using Tcl/TK

from tkinter import *
from tkinter import ttk

root = Tk()                         # Create a tkinter window
root.title("Welcome ")

frm1 = ttk.Frame(root, padding=10)
root.geometry('400x300')            # Open window having dimension 400x300
frm1.grid(row=0, column=0)
l1 = Label(frm1, text="Hello World ")
l1.grid(row=0, column=1)

btn1 = Button(frm1, text="Ok")
#btn1.pack()                        # The layout manager stacks widgets on the top of each other verically like blocks
                                    # They can be arranged horizontally by side=left/right  
btn1.grid(row=2, column=0)          # Works similar to a matrix, row & column

btn_exit = Button(frm1, text="EXIT", command = root.destroy)
btn_exit.grid(row=2, column=1)


root.mainloop()