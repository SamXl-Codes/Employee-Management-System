# GUI -1
# Choose elective modules

from tkinter import *
from tkinter import ttk

root = Tk()
root.geometry('600x300')
root.title('Elective modules')
val1 = IntVar()
val2 = IntVar()
val3 = IntVar()
val4 = IntVar()

l1 = Label(root, text="Select any 2 languages you want to study in the upcoming semester")
l1.grid(row=1, column=0)
ch_btn1 = Checkbutton(root, text='Python', variable=val1).grid(row=2,column=0, sticky=W)  #sticky indicates which side of the cell the widget sticks to.
ch_btn2 = Checkbutton(root, text='C#', variable=val2).grid(row=3,column=0, sticky=W)
ch_btn3 = Checkbutton(root, text='JavaScript', variable=val3).grid(row=4,column=0, sticky=W)
ch_btn4 = Checkbutton(root, text='R', variable=val4).grid(row=5,column=0, sticky=W)

def show():
    if val1.get() == True:
        print("Python")
    if  val2.get() == True:
        print("C# ")
    if val3.get() == True:
        print("JavaScript ")
    if val4.get() == True:
        print("R ")
    print(combo1.get())
    
btn_show = Button(root, text="Show",width=10, command= lambda: show())
btn_show.grid(row=8,column=0)

btn_exit = Button(root, text="EXIT", command = root.destroy)
btn_exit.grid(row=8, column=1)


#languages = StringVar()
languages = ['Sem-1','Sem-2','Sem-3']
combo1 = ttk.Combobox(root, state='readonly')
combo1['values']=('Sem-1','Sem-2','Sem-3')
combo1.current(1)

#combo1.set(languages)
combo1.grid(row=6, column=0)

root.mainloop()