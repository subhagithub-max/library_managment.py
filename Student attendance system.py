import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
from datetime import datetime

# Database
connector = sqlite3.connect('Attendance.db')
cursor = connector.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Attendance (
    ROLL_NO TEXT PRIMARY KEY,
    NAME TEXT,
    DATE TEXT,
    STATUS TEXT,
    REMARKS TEXT
)
''')

# Functions
def display_records():
    tree.delete(*tree.get_children())
    data = cursor.execute("SELECT * FROM Attendance").fetchall()
    for row in data:
        tree.insert('', END, values=row)

def clear_fields():
    roll_no.set('')
    name.set('')
    date.set(datetime.now().strftime("%Y-%m-%d"))
    status.set('Present')
    remarks.set('')

def add_record():
    try:
        cursor.execute('INSERT INTO Attendance VALUES (?, ?, ?, ?, ?)', 
                       (roll_no.get(), name.get(), date.get(), status.get(), remarks.get()))
        connector.commit()
        display_records()
        mb.showinfo("Success", "Attendance record added successfully!")
        clear_fields()
    except sqlite3.IntegrityError:
        mb.showerror("Error", "Roll number already exists!")

def view_record():
    if not tree.selection():
        mb.showerror("Error", "Please select a record to view")
        return
    selected = tree.item(tree.selection()[0])['values']
    roll_no.set(selected[0])
    name.set(selected[1])
    date.set(selected[2])
    status.set(selected[3])
    remarks.set(selected[4])

def update_record():
    if not roll_no.get():
        mb.showerror("Error", "Roll number required to update")
        return
    cursor.execute("UPDATE Attendance SET NAME=?, DATE=?, STATUS=?, REMARKS=? WHERE ROLL_NO=?",
                   (name.get(), date.get(), status.get(), remarks.get(), roll_no.get()))
    connector.commit()
    display_records()
    mb.showinfo("Updated", "Record updated successfully")
    clear_fields()

def delete_record():
    if not tree.selection():
        mb.showerror("Error", "Select a record to delete")
        return
    selected = tree.item(tree.selection()[0])['values']
    cursor.execute("DELETE FROM Attendance WHERE ROLL_NO=?", (selected[0],))
    connector.commit()
    display_records()
    mb.showinfo("Deleted", "Record deleted successfully")
    clear_fields()

def search_record():
    keyword = sd.askstring("Search", "Enter Roll No to search:")
    if not keyword:
        return
    data = cursor.execute("SELECT * FROM Attendance WHERE ROLL_NO=?", (keyword,)).fetchone()
    if data:
        tree.delete(*tree.get_children())
        tree.insert('', END, values=data)
    else:
        mb.showinfo("Not Found", "No record found with this Roll No")

# GUI
root = Tk()
root.title("Student Attendance Management")
root.geometry("1440x600")

# Top banner
Label(root, text="📚 Student Attendance Management System",
      font=("Arial", 18, "bold"), bg="#00b4d8", fg="white").pack(side=TOP, fill=X)

# Variables
roll_no = StringVar()
name = StringVar()
date = StringVar(value=datetime.now().strftime("%Y-%m-%d"))
status = StringVar(value="Present")
remarks = StringVar()

# Frames with colors
left_frame = Frame(root, bg="#caf0f8")
left_frame.place(x=0, y=40, relwidth=0.3, relheight=0.96)

right_frame = Frame(root, bg="#f1faee")
right_frame.place(relx=0.3, y=40, relwidth=0.7, relheight=0.96)

# Left Frame Form
Label(left_frame, text="Roll No:", font=("Arial", 12, "bold"), bg="#caf0f8").place(x=40, y=40)
Entry(left_frame, textvariable=roll_no, font=("Arial", 12), bg="white").place(x=40, y=70)

Label(left_frame, text="Name:", font=("Arial", 12, "bold"), bg="#caf0f8").place(x=40, y=110)
Entry(left_frame, textvariable=name, font=("Arial", 12), bg="white").place(x=40, y=140)

Label(left_frame, text="Date:", font=("Arial", 12, "bold"), bg="#caf0f8").place(x=40, y=180)
Entry(left_frame, textvariable=date, font=("Arial", 12), bg="white").place(x=40, y=210)

Label(left_frame, text="Status:", font=("Arial", 12, "bold"), bg="#caf0f8").place(x=40, y=250)
OptionMenu(left_frame, status, "Present", "Absent", "Late").place(x=40, y=280)

Label(left_frame, text="Remarks:", font=("Arial", 12, "bold"), bg="#caf0f8").place(x=40, y=320)
Entry(left_frame, textvariable=remarks, font=("Arial", 12), bg="white").place(x=40, y=350)

# Buttons with colors
btn_style = {"width": 20, "font": ("Arial", 11, "bold")}

Button(left_frame, text="➕ Add Record", bg="#06d6a0", fg="white", command=add_record, **btn_style).place(x=40, y=390)
Button(left_frame, text="✏ Update Record", bg="#ffd166", fg="black", command=update_record, **btn_style).place(x=40, y=430)
Button(left_frame, text="🧹 Clear Fields", bg="#ef476f", fg="white", command=clear_fields, **btn_style).place(x=40, y=470)

# Right Frame Treeview
Label(right_frame, text="📋 Attendance Records", font=("Arial", 14, "bold"),
      bg="#90e0ef", fg="black").pack(side=TOP, fill=X)

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview",
                background="white",
                foreground="black",
                rowheight=25,
                fieldbackground="white")
style.map("Treeview", background=[("selected", "#48cae4")])

tree = ttk.Treeview(right_frame, columns=("Roll No", "Name", "Date", "Status", "Remarks"), show="headings")
tree.heading("Roll No", text="Roll No")
tree.heading("Name", text="Name")
tree.heading("Date", text="Date")
tree.heading("Status", text="Status")
tree.heading("Remarks", text="Remarks")
tree.pack(fill=BOTH, expand=True, pady=10, padx=10)

# Striped row colors
tree.tag_configure("oddrow", background="#f8f9fa")
tree.tag_configure("evenrow", background="#e9ecef")

def refresh_tree():
    tree.delete(*tree.get_children())
    rows = cursor.execute("SELECT * FROM Attendance").fetchall()
    for i, row in enumerate(rows):
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tree.insert('', END, values=row, tags=(tag,))

refresh_tree()

scrollbar_y = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar_y.set)
scrollbar_y.pack(side=RIGHT, fill=Y)

# Buttons on right frame
btn_right = {"font": ("Arial", 11, "bold"), "width": 16, "pady": 5}

Button(right_frame, text="👁 View Record", bg="#06d6a0", fg="white", command=view_record, **btn_right).pack(side=LEFT, padx=10, pady=10)
Button(right_frame, text="❌ Delete Record", bg="#ef476f", fg="white", command=delete_record, **btn_right).pack(side=LEFT, padx=10, pady=10)
Button(right_frame, text="🔍 Search Roll No", bg="#118ab2", fg="white", command=search_record, **btn_right).pack(side=LEFT, padx=10, pady=10)

# Load records
display_records()

root.mainloop()
