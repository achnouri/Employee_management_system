import sqlite3

class DataB:
    def __init__(self, db):

        self.con = sqlite3.connect(db)
        self.cur = self.con.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS employees(
                id INTEGER PRIMARY KEY,
                name TEXT,
                gender TEXT,
                age TEXT,
                job TEXT,
                email TEXT UNIQUE,
                mobile TEXT UNIQUE,
                status TEXT,
                address TEXT
            )
        """)
        self.con.commit()

    def insert(self, name, gender, age, job, email, mobile, status, address):
        self.cur.execute("INSERT INTO employees (name, gender, age, job, email, mobile, status, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, gender, age, job, email, mobile, status, address))
        self.con.commit()

    def fetch(self):
        self.cur.execute("SELECT * FROM employees")
        return self.cur.fetchall()

    def remove(self, emp_id):
        self.cur.execute("DELETE FROM employees WHERE id=?", (emp_id,))
        self.con.commit()

    def update(self, emp_id, name, gender, age, job, email, mobile, status, address):
        self.cur.execute("UPDATE employees SET name=?, gender=?, age=?, job=?, email=?, mobile=?, status=?, address=? WHERE id=?", (name, gender, age, job, email, mobile, status, address, emp_id))
        self.con.commit()

    def count_employees(self):
        self.cur.execute("SELECT COUNT(*) FROM employees")
        return self.cur.fetchone()[0]

    def search(self, search_term):
        self.cur.execute(""" SELECT * FROM employees WHERE name LIKE ? OR job LIKE ? OR email LIKE ? OR mobile LIKE ?""", (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        return self.cur.fetchall()

    def username_exists(self, name):
        self.cur.execute("SELECT id FROM employees WHERE name=?", (name,))
        return self.cur.fetchone() is not None
    
    def __del__(self):
        self.con.close()