from tkinter import *
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from  employee_system_db import DataB
import sqlite3
import time
import os
import re
import hashlib
import binascii
import csv

signin_form_window = Tk()
signin_form_window.title("Employee Management System - Sign In Form")
signin_form_window.geometry("925x500+300+200")
signin_form_window.resizable(False, False)
signin_form_window.configure(bg="#fff")

def initialize_db():
    conn = sqlite3.connect("database_form.db")
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users 
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            userpassword TEXT NOT NULL
        )
        '''
    )
    
    cursor.execute("SELECT * FROM users WHERE username = 'achnouri'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, userpassword) VALUES (?, ?)", ('achnouri', 'pass_123'))

    conn.commit()
    conn.close()

try:
    initialize_db()
except:
    print("Database initialization failed : {e}")

def lanuch_employee_system():
    sign_in_exit()
    db = DataB("Employee.db")

    main = Tk()
    main.title('Employee management system project')
    main.geometry('1800x720+35+120')
    main.resizable(True, False)
    main.configure(bg='#34495E')

    name = StringVar(main)
    gender = StringVar(main)
    age = StringVar(main)
    job = StringVar(main)
    email = StringVar(main)
    mobile = StringVar(main)
    status = StringVar(main)
    address = StringVar(main)
    selected_row = None
    search_bar = StringVar(main)

    def hide_frame_b():
        main.geometry('400x720+20+80')

    def show_frame_b():
        main.geometry('1800x720+20+80')

    def exit_all():
        main.destroy()
        
    def update_employee_count():
        employee_count = db.count_employees()
        employee_count_label.configure(text=f"Total Employees: {employee_count}")

    def validate_entries():
        current_name = name.get().strip()
        current_gender = gender.get().strip().lower()
        current_age = age.get().strip()
        current_job = job.get().strip()
        current_email = email.get().strip()
        current_mobile = mobile.get().strip()
        current_status = status.get().strip().lower()
        current_address = address.get().strip()
        
        if not all([current_name, current_gender, current_age, current_job, current_email, current_mobile, current_status, current_address]):
            messagebox.showerror("ERROR", "Fill all fields")
            return False
            
        if current_gender not in ["male", "female"]:
            messagebox.showerror("ERROR", "Gender must be 'Male' or 'Female'")
            return False
            
        if not current_age.isdigit():
            messagebox.showerror("Error", "Age must be a number")    
            return False
            
        age_num = int(current_age)
        if age_num < 18 or age_num > 100:
            messagebox.showerror("Error", "Age must be between 18 and 100")
            return False
            
        if len(current_mobile) != 10 or not current_mobile.isdigit():
            messagebox.showerror("Error", "Mobile number must be 10 digits")
            return False
            
        if "@" not in current_email or "." not in current_email:
            messagebox.showerror("ERROR", "Invalid email format")
            return False
            
        if current_status not in ["true", "false"]:
            messagebox.showinfo("Info", "Status must be 'true' or 'false'")    
            return False
            
        return True

    def add_employee():
        if not validate_entries():
            return

        response = messagebox.askquestion( "Confirm Add", f"Do you want to add this new employee?\n\n" f"Name : {name.get()}\n" f"Gender : {gender.get()}\n" f"Age : {age.get()}\n" f"Job : {job.get()}\n" f"Email: {email.get()}\n" f"Mobile : {mobile.get()}\n"  f"Status : {status.get()}\n" f"Address : {address.get()}\n",icon='question')
        
        if response == 'yes':
            try:
                db.insert(name.get(), gender.get(), age.get(), job.get(), email.get(), mobile.get(), status.get(), address.get())
                messagebox.showinfo("Success", "Employee added successfully")
                display_all()
                clear_form()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to add employee: {str(e)}")
        else:
            messagebox.showinfo("Cancelled", "Employee was not added")

    def update_employee():
        if not selected_row:
            messagebox.showerror("Error", "Select an employee to update")
            return

        if not validate_entries():
            return

        try:
            db.update(selected_row[0], name.get(), gender.get(), age.get(), job.get(), email.get(), mobile.get(), status.get(), address.get())
            messagebox.showinfo("Success", "Employee updated successfully")
            display_all()
            clear_form()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update employee: {str(e)}")

    def delete_employee():
        if not selected_row:
            messagebox.showerror("Error", "Select an employee to delete")
            return

        try:
            response = messagebox.askquestion( "Confirm Delete", f"Do you want to delete this employee \n\n Id: {selected_row[0]}?\n Name: {selected_row[1]}\n\n ", icon='warning')

            if response == 'yes':
                db.remove(selected_row[0])
                messagebox.showinfo("Success", "Employee deleted successfully")
                display_all()
                clear_form()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete employee: {str(e)}")

    def clear_form():
        nonlocal selected_row
        name.set("")
        gender.set("")
        age.set("")
        job.set("")
        email.set("")
        mobile.set("")
        status.set("")
        address.set("")
        selected_row = None

    def display_all():
        tv.delete(*tv.get_children())
        for row in db.fetch():
            tv.insert("", END, values=row)
        update_employee_count()

    def search_employee():
        query = search_bar.get().strip()
        tv.delete(*tv.get_children())

        if not query:
            display_all()
            return

        res = db.search(query)

        for row in res:
            tv.insert("", END, values=row)

        if not res:
            messagebox.showinfo("Search", "No employees found matching your search")

    def export_details_to_csv():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save employee data as CSV"
        )

        if not file_path:
            return
        try:
            employees = db.fetch()

            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Name", "Gender", "Age", "Job", "Email", "Mobile", "Status", "Address", "Salary", "Department"])
                writer.writerows(employees)

            messagebox.showinfo("Success", f"Data exported to {file_path}")

            log_action(user_id, "export_data", f"Exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def get_selected_data(event):
        nonlocal selected_row
        selected = tv.focus()
        data = tv.item(selected, 'values')

        if data:
            selected_row = data
            name.set(data[1])
            gender.set(data[2])
            age.set(data[3])
            job.set(data[4])
            email.set(data[5])
            mobile.set(data[6])
            status.set(data[7])
            address.set(data[8])

    frame_a = Frame(main, bg='#34495E')
    frame_a.place(x=0,y=0, width=400, height=800)
    title_frame_a = Label(frame_a, text="Employee Company", font=('Calibri',16,'bold'), bg='#34495E', fg='orange')
    title_frame_a.place(x=10,y=7)

    form_fields = [("Name", name), ("Gender", gender), ("Age", age), ("Job", job), ("Mobile", mobile), ("Email", email), ("Status", status), ("Address", address)]
    y_offset = 57

    for label_text_form, var  in form_fields:
        lable = Label(frame_a, text=label_text_form, font=('Calibri', 14, 'bold'), fg='white', bg="#2c3e50")
        lable.place(x=5, y=y_offset)
        entry = Entry(frame_a, textvariable=var, width=25,font=('Calibri', 13), fg="white", bg= "#5D6D7E")
        entry.place(x=100, y=y_offset)
        y_offset += 50

    button_hide_frame_b = Button(frame_a, text="Hide",bg='#34495E',bd=1,relief=SOLID,cursor="hand2",command=hide_frame_b)
    button_hide_frame_b.place(x=70,y=650)

    button_show_frame_b = Button(frame_a, text="Show",bg='#34495E',bd=1,relief=SOLID,cursor="hand2",command=show_frame_b)
    button_show_frame_b.place(x=170,y=650)

    button_exit_all = Button(frame_a, text="Exit", bg='#34495E', bd=1, relief=SOLID, cursor="hand2", command=exit_all)
    button_exit_all.place(x=270,y=650)

    buttons_form_frame = Frame(frame_a, bg='#2c3e50', bd=1, relief=SOLID)
    buttons_form_frame.place(x=5,y=470, width=381, height=150)

    button_add_form = Button(buttons_form_frame, text="Add Details", width=11 ,height=1 ,font=('Calibri', 13) ,fg='white' ,bg='#16a085',bd=0, command= add_employee)
    button_add_form.place(x=4, y=7)

    button_update_form = Button(buttons_form_frame, text="Update Details", width=11 ,height=1 ,font=('Calibri', 13) ,fg='white' ,bg='#2980b9',bd=0, command= update_employee)
    button_update_form.place(x=4, y=55)
  
    button_delete_form = Button(buttons_form_frame, text="Delete Details", width=11 ,height=1 ,font=('Calibri', 13) ,fg='white' ,bg='#c0329b',bd=0, command= delete_employee)
    button_delete_form.place(x=220, y=7)
    
    button_clear_form = Button(buttons_form_frame, text="Clear Details", width=11 ,height=1 ,font=('Calibri', 13) ,fg='white' ,bg='#f39c12',bd=0, command= clear_form)
    button_clear_form.place(x=220, y=55)

    button_export = Button(buttons_form_frame, text="Export Details", width=33 ,height=1 ,font=('Calibri', 13) ,fg='white' ,bg='orange',bd=0, command= export_details_to_csv)
    button_export.place(x=0, y=114)

    frame_b = Frame(main, bg='white')
    frame_b.place(x=400,y=0,width=1700,height=700)

    style_a = ttk.Style()
    style_a.theme_use('default')

    style_a.configure("mystyle.Treeview", font=('Calibri', 10), rowheight=41, background="#f8f9fa", foreground="black", fieldbackground="#f8f9fa",bordercolor="#dee2e6",  borderwidth=1)          

    style_a.configure("mystyle.Treeview.Heading", font=('Calibri', 12, 'bold'), background="#343a40", foreground="white",   relief="flat")    

    style_a.map("mystyle.Treeview",background=[('selected', '#007bff')], foreground=[('selected', 'white')]) 

    tv = ttk.Treeview(frame_b, columns=(1, 2, 3, 4, 5, 6, 7, 8, 9), style="mystyle.Treeview", selectmode="browse")

    tv.heading("1", text="ID")
    tv.column("1", width="25", anchor='center')

    tv.heading("2", text="Name")
    tv.column("2", width="100")

    tv.heading("3", text="Gender")
    tv.column("3", width="75", anchor='center')

    tv.heading("4", text="Age")
    tv.column("4", width="30", anchor='center')

    tv.heading("5", text="Job")
    tv.column("5", width="175")

    tv.heading("6", text="Email")
    tv.column("6", width="210")

    tv.heading("7", text="Mobile")
    tv.column("7", width="90")

    tv.heading("8", text="Status")
    tv.column("8", width="70", anchor='center')

    tv.heading("9", text="Address")
    tv.column("9", width="310")

    tv['show'] = 'headings'
    tv.bind("<ButtonRelease-1>", get_selected_data)
    tv.place(x=0, y=0, height=715, width=1400)

    status_bar = Frame(main, bg="#2c3e50")
    status_bar.place(x=400, y=650, width=1400, height=70)

    search_bar = Entry(status_bar, textvariable=search_bar, bg="#5D6D7E", fg="white",insertbackground="white") 
    search_bar.place(x=5, y=10, width=1305, height=25)

    button_search = Button(status_bar, text="Search", bg='#34495E', bd=1,relief=SOLID, cursor="hand2", command=search_employee, activebackground="#495057", activeforeground="white")
    button_search.place(x=1320, y=8)

    employee_count_label = Label(status_bar, text="", font=('Calibri', 10, 'bold'), fg='orange', bg="#2c3e50")
    employee_count_label.place(x=5, y=40)
    display_all()

    main.bind('<Control-n>', lambda e: add_employee())
    main.bind('<Control-s>', lambda e: search_employee())
    main.bind('<Control-q>', lambda e: exit_all())

    main.mainloop()

def verify_password(username, stored_password, entered_password):
    return stored_password == entered_password

def sign_in():

    def error_label_msg(error_message):
            error_login_label = Label(frame_a, text=f"{error_message}", bg="#f6e1e1", fg= "red",font=  ("Calibri", 8))
            error_login_label.place(x=32, y=285)
            error_login_label.after(5000, error_login_label.destroy)

    user_name_value = user_name_signin.get()
    user_password_value = user_password_signin.get()
    
    if not user_name_value or not user_password_value:
        error_label_msg("ERROR !, Fill all entries")
        return

    def fetch_user_data():
        conn = sqlite3.connect("database_form.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (user_name_value,))
        user_data = cursor.fetchone()
        conn.close()

        return user_data

    def display_success_login_message():
        success_login_label = Label(frame_a, text=f"Welcome {user_name_value}, logging in...", bg="#5ef269", font=  ("Calibri", 9, 'bold'))
        success_login_label.place(x=50, y=285)
    
    def show_progress_success_login():
        #progress = ttk.Progressbar(frame_a, orient=HORIZONTAL, length=300, mode='indeterminate')
        #progress.place(x=30, y=250)
        #progress.start()
        display_success_login_message()
        #progress.stop()
        #signin_form_window.destroy()
            

    def success_login(user_data):
        if user_data and verify_password(user_data[1], user_data[2], user_password_value):
            display_success_login_message()
            signin_form_window.after(3000, lanuch_employee_system)

        else:
            #messagebox.showerror("ERROR !", "Invalid User Name or User Password !")
            error_label_msg("ERROR! Invalid User Name or User Password !")

    user_data = fetch_user_data()
    success_login(user_data)

def sign_up():

    def error_label_msg(error_message):
            error_login_label = Label(frame_b, text=f"{error_message}", bg="#f6e1e1", fg= "red", font=  ("Calibri", 8))
            error_login_label.place(x=32, y=320)
            error_login_label.after(5000, error_login_label.destroy)

    def success_label_msg(success_message):
            success_login_label = Label(frame_b, text=f"{success_message}", bg="#5ef269", font=  ("Calibri", 8))
            success_login_label.place(x=32, y=320)
            success_login_label.after(5000, error_login_label.destroy)

    def validate_registration(username, password, confirmpassw):
        
        if not ([username, password, confirmpassw]):
            #messagebox.showerror("ERROR", "All fields must be filled")
            error_label_msg("ERROR ! ,Invalid User Name or User Password !")
            return False
        
        if len(username) < 4:
            #messagebox.showerror("ERROR", "Username must be at least 4 characters")
            error_label_msg("ERROR ! ,Invalid User Name or User Password !")
            return False
        
        if ' ' in username:
            #messagebox.showerror("ERROR", "Username cannot contain spaces")
            error_label_msg("ERROR ! ,Invalid User Name or User Password !")
            return False
        
        if not username.isalnum():
            #messagebox.showerror("ERROR", "Username can only contain letters and numbers")
            error_label_msg("ERROR, Username can only contain letters and numbers")
            return False
        
        if len(password) < 8:
            #messagebox.showerror("ERROR", "Password must be at least 8 characters")
            error_label_msg("ERROR, Password must be at least 8 characters")
            return False

        if not re.search(r"[A-Z]", password):
            #messagebox.showerror("ERROR", "Password must contain at least one uppercase letter")
            error_label_msg("ERROR, Password must contain at least one uppercase letter")
            return False
        
        if not re.search(r"[a-z]", password):
            #messagebox.showerror("ERROR", "Password must contain at least one lowercase letter")
            error_label_msg("ERROR, Password must contain at least one lowercase letter")
            return False
        
        if not re.search(r"[0-9]", password):
            #messagebox.showerror("ERROR", "Password must contain at least one number")
            error_label_msg("ERROR, Password must contain at least one number")
            return False
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            #messagebox.showerror("ERROR", "Password must contain at least one special character")
            error_label_msg("ERROR, Password must contain at least one special character")
            return False

        weak_passwords = [
            "password", "123456", "12345678", "123456789", "12345","1234567", "1234567890", "qwerty", "abc123", "password1",
            "123123", "000000", "iloveyou", "111111", "admin","welcome", "monkey", "sunshine", "letmein", "1234",
            "123", "1234", "12345", "123456", "1234567", "12345678", "123456789", "1234567890", "0123456789",
            "qwerty", "qwerty123", "qwertyuiop", "asdfghjkl", "zxcvbnm","1qaz2wsx", "1q2w3e4r", "1q2w3e4r5t", "qazwsx", "password123",
            "hello123", "welcome123", "admin123", "test123", "guest123","temp123", "pass123", "access123", "changeme123", "letmein123",
            "default", "user", "root", "administrator", "login","passw0rd", "pass", "pw", "p@ssword", "p@ssw0rd",
            "superman", "batman", "starwars", "pokemon", "harrypotter","matrix", "ironman", "freedom", "shadow", "master",
            "football", "soccer", "baseball", "basketball", "hockey","runner", "swimmer", "golfer", "tennis", "cricket",
            "iloveyou", "ihateyou", "trustno1", "loveme", "hello","whatever", "nothing", "something", "everything", "nobody",
            "summer", "winter", "spring", "fall", "january","february", "monday", "tuesday", "2023", "2024",
            "wifi", "internet", "computer", "laptop", "smartphone","google", "facebook", "youtube", "instagram", "twitter",
            "dragon", "butterfly", "eagle", "tiger", "lion","cat", "dog", "fish", "bird", "snake","coffee", "tea", "pizza", "burger", "chocolate","banana", "apple", "orange", "beer", "wine"
            ]
    
        if password.lower() in weak_passwords:
            #messagebox.showerror("ERROR", "Password is too common - choose a stronger one")
            error_label_msg("ERROR", "Password is too common - choose a stronger one")
            return False
        
        if password != confirmpassw:
            #messagebox.showerror("ERROR", "Passwords do not match")
            error_label_msg("ERROR", "Passwords do not match")
            return False
        
        return True
    
    def sign_up_cmd():
        
        username = user_name_signup.get()
        password = user_password_signup.get()
        confirm_password = user_password_confirm_signup.get()

        if not validate_registration(username, password, confirm_password):
            return

        conn = None
        try:
            conn = sqlite3.connect("database_form.db")
            cursor = conn.cursor()

            cursor.execute("SELECT username FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                #messagebox.showerror("Error", "Username already exists")
                error_label_msg("Error, Username already exists")
                return
                
            cursor.execute("INSERT INTO users (username, userpassword) VALUES (?, ?)", (username, password))
            
            conn.commit()
            conn.close()
            #messagebox.showinfo("Success", "Registration successfull")
            success_label_msg("Success", "Registration successfull")
        except Exception as er:
            #messagebox.showerror("Error", f"Registration failed : {str(er)}")
            error_label_msg(f"Registration failed : {str(er)}")
        finally:
            if conn:
                conn.close()

    def on_enter_user_name(e):
        user_name_signup.delete(0, "end")

    def on_leave_user_name(e):
        get_un = user_name_signup.get()
        if get_un == "":
            user_name_signup.insert(0, "User Name") 

    def on_enter_user_password(e):
        user_password_signup.delete(0, "end")

    def on_leave_user_password(e):
        get_up = user_password_signup.get()
        if get_up == "":
            user_password_signup.insert(0, "Password")

    def on_enter_user_confirm_password(e):
        user_password_confirm_signup.delete(0, "end")

    def on_leave_user_confirm_password(e):
        get_up = user_password_confirm_signup.get()
        if get_up == "":
            user_password_confirm_signup.insert(0, "Confirm Password")

    def sign_in_cmd():
        signup_form_window.destroy()

    def sign_up_exit():
        #if messagebox.askokcancel("Quit", "Do you want to exit the application?"):
        signup_form_window.destroy()
        sign_in_exit()

    def sign_up_back():
        signup_form_window.destroy()

    signup_form_window = Toplevel(signin_form_window)
    signup_form_window.title("Employee Management System - Sign Up")
    signup_form_window.geometry("925x500+300+200")
    signup_form_window.resizable(False, False)
    signup_form_window.configure(bg="#fff")

    frame_b = Frame(signup_form_window, width= 450, height= 450, bg= "white")
    frame_b.place(x= 480, y= 70)

    head_b_txt = Label(frame_b, text= "Sign Up", fg= "#57a1f8", bg='white', font= ("Microsoft YaHei UI  Light", 23, 'bold'))
    head_b_txt.place(x= 100,y= 5)

    user_name_signup = StringVar()
    user_password_signup = StringVar()
    user_password_confirm_signup = StringVar()

    user_name_signup = Entry(frame_b, textvariable=user_name_signup, width= 30, fg= "black", bg= "white",bd= 0, font= ("Microsoft YaHei UI     Light", 11))
    user_name_signup.place(x= 30, y= 80)
    user_name_signup.insert(0, "User Name")
    user_name_signup.bind("<FocusIn>", on_enter_user_name)
    user_name_signup.bind("<FocusOut>", on_leave_user_name)

    user_password_signup = Entry(frame_b, textvariable=user_password_signup, width= 30, fg= "black", bg= "white",bd= 0, font= ("Microsoft YaHei    UI Light", 11),  show= "*")
    user_password_signup.place(x= 30, y= 150)
    user_password_signup.insert(0, "Password")
    user_password_signup.bind("<FocusIn>", on_enter_user_password)
    user_password_signup.bind("<FocusOut>", on_leave_user_password)

    user_password_confirm_signup = Entry(frame_b, textvariable=user_password_confirm_signup, width= 30, fg= "black", bg= "white",bd= 0, font= ("Microsoft YaHei    UI Light", 11), show= "*")
    user_password_confirm_signup.place(x= 30, y= 220)
    user_password_confirm_signup.insert(0, "Confirm Password")
    user_password_confirm_signup.bind("<FocusIn>", on_enter_user_confirm_password)
    user_password_confirm_signup.bind("<FocusOut>", on_leave_user_confirm_password)
    
    signup_button_signin = Button(frame_b,text= "Sign Up", width= 31, pady= 1,fg= "#57a1f8", bg= "#e8f3fa", bd= 0, cursor= "hand2", command= sign_up_cmd)
    signup_button_signin.place(x= 30,y= 290)

    signup_button_back = Button(frame_b,text= "Back", width= 10, pady= 1, fg= "#57a1f8", bg= "white", bd= 0,  cursor= "hand2", command= sign_up_back)
    signup_button_back.place(x= 30,y= 390)
    
    signup_button_signup = Button(frame_b,text= "Sign In", width= 10, pady= 1, fg= "#57a1f8", bg= "white", bd= 0,  cursor= "hand2", command= sign_in_cmd)
    signup_button_signup.place(x= 165,y= 390)
    
    signup_button_exit = Button(frame_b,text= "Exit", width= 10, pady= 1, fg= "#57a1f8", bg= "white", bd= 0,  cursor= "hand2", command= sign_up_exit)
    signup_button_exit.place(x= 300,y= 390)

    try:
        signin_signup_img = PhotoImage(file= "images/signup.png")
        Label(signup_form_window, image= signin_signup_img, bg= "white").place(x=50, y = 50)
    except:
        Label(signup_form_window, text="image(error in display)", bg= "white").place(x=50, y = 50)

    signup_form_window.mainloop()

try:
    signin_signup_img = PhotoImage(file= "images/signin.png")
    Label(signin_form_window, image= signin_signup_img, bg= "white").place(x=50, y = 50)
except:
    Label(signin_form_window, text="image(error in display)", bg= "white").place(x=50, y = 50)

def on_enter_user_name(e):
    user_name_signin.delete(0, "end")

def on_leave_user_name(e):
    get_un = user_name_signin.get()
    if get_un == "":
        user_name_signin.insert(0, "User name") 

def on_enter_user_password(e):
    user_password_signin.delete(0, "end")

def on_leave_user_password(e):
    get_up = user_password_signin.get()
    if get_up == "":
        user_password_signin.insert(0, "User password")

def sign_in_exit():
    #if messagebox.askokcancel("Quit", "Do you want to exit the application?"):
    signin_form_window.destroy()

#def hash_password(password, salt=None):
    #if not salt:
        #salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    #passw = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 1000000)
    #passw = binascii.hexlify(pwdhash)
    #return salt, (salt + passw).encode('ascii')

frame_a = Frame(signin_form_window, width= 450, height= 450, bg= "white")
frame_a.place(x= 480, y= 70)

head_a_txt = Label(frame_a, text= "Sign In", fg= "#57a1f8", bg='white', font= ("Microsoft YaHei UI Light", 23, 'bold'))
head_a_txt.place(x= 100,y= 5)

user_name_signin = Entry(frame_a, width= 30, fg= "black", bg= "white",bd= 0, font= ("Microsoft YaHei UI Light", 11))
user_name_signin.place(x= 30, y= 80)
user_name_signin.insert(0, "User name")
user_name_signin.bind("<FocusIn>", on_enter_user_name)
user_name_signin.bind("<FocusOut>", on_leave_user_name)

user_password_signin = Entry(frame_a, width= 30, fg= "black", bg= "white",bd= 0, font= ("Microsoft YaHei UI Light", 11), show="*")
user_password_signin.place(x= 30, y= 150)
user_password_signin.insert(0, "User password")
user_password_signin.bind("<FocusIn>", on_enter_user_password)
user_password_signin.bind("<FocusOut>", on_leave_user_password)

signin_button_signin = Button(frame_a,text= "Sign In", width= 31, pady= 1,fg= "#57a1f8", bg= "#e8f3fa", bd= 0, cursor= "hand2", command= sign_in)
signin_button_signin.place(x= 30,y= 220)

note_txt_signin = Label(frame_a, text= "Don't have an account ? >>", bg= "white", fg= "black", font= ("Microsoft YaHei UI Light", 8))
note_txt_signin.place(x= 27, y= 392)

signup_button_signin = Button(frame_a,text= "Sign Up", width= 10, pady= 1, fg= "#57a1f8", bg= "white", bd= 0, cursor= "hand2", command= sign_up)
signup_button_signin.place(x= 190,y= 390)

exit_button_signin = Button(frame_a,text= "Exit", width= 10, pady= 1, fg= "#57a1f8", bg= "white", bd= 0, cursor= "hand2", command= sign_in_exit)
exit_button_signin.place(x= 320,y= 390)

signin_form_window.mainloop()


#CREATED BY ACHNOURI