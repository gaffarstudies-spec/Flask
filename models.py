import mysql.connector
from datetime import datetime

# MySQL database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",        # <-- Replace with your MySQL username
    "password": "Admin@123", # <-- Replace with your MySQL password
    "database": "finance_tracker"
}

def connect_db():
    """Connect to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)

# ---------------- USER FUNCTIONS ----------------
def register_user(username, password):
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return True, "Registration successful!"
    except mysql.connector.IntegrityError:
        return False, "Username already exists!"
    finally:
        cursor.close()
        db.close()

def login_user(username, password):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user

# ---------------- TRANSACTION FUNCTIONS ----------------
def add_transaction(user_id, t_type, amount, category, description, date_str):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, type, amount, category, description, date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, t_type, amount, category, description, date_str))
    db.commit()
    cursor.close()
    db.close()

def get_transactions(user_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions WHERE user_id=%s ORDER BY date DESC", (user_id,))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

def get_summary(user_id, year, month):
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT type, SUM(amount) FROM transactions
        WHERE user_id=%s AND YEAR(date)=%s AND MONTH(date)=%s
        GROUP BY type
    """, (user_id, year, month))

    data = cursor.fetchall()
    cursor.close()
    db.close()

    income = expense = 0
    for row in data:
        if row[0] == 'income':
            income = row[1]
        elif row[0] == 'expense':
            expense = row[1]

    balance = income - expense
    return income, expense, balance
