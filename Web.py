from flask import Flask, request, redirect, url_for, session, render_template_string, send_file
import mysql.connector
from datetime import datetime
import hashlib
import io
import csv

# ------------------ MySQL Config ------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",         # <-- Replace with your MySQL username
    "password": "Admin@123",# <-- Replace with your MySQL password
    "database": "finance_tracker"
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

# ------------------ Password Hashing ------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------ Flask App ---------------------
app = Flask(__name__)
app.secret_key = "my_secret_key_123"  # Session key

# ------------------ HTML + CSS ---------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Personal Finance Tracker</title>
    <style>
        /* Global Reset */
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(120deg, #6a11cb, #2575fc);
            color: #333;
            min-height: 100vh;
        }

        h2, h3 {
            color: #333;
        }

        /* Container Card */
        .container {
            margin: 40px auto;
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            width: 400px;
            text-align: center;
        }

        /* Menu bar */
        .menu {
            background: white;
            padding: 10px;
            border-radius: 8px;
            width: 90%;
            margin: 20px auto;
            display: flex;
            justify-content: center;
            gap: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }

        .menu a {
            padding: 8px 15px;
            background: #2575fc;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            transition: 0.3s;
        }

        .menu a:hover {
            background: #6a11cb;
        }

        /* Form Styling */
        input, select, button {
            margin: 8px 0;
            padding: 10px;
            width: 90%;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 15px;
            transition: 0.3s;
        }

        input:focus, select:focus {
            border-color: #2575fc;
            outline: none;
            box-shadow: 0 0 8px rgba(37,117,252,0.4);
        }

        button {
            background: #2575fc;
            color: white;
            border: none;
            cursor: pointer;
        }

        button:hover {
            background: #6a11cb;
        }

        /* Table */
        table {
            margin: 20px auto;
            border-collapse: collapse;
            width: 90%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        th {
            background: #2575fc;
            color: white;
            padding: 12px;
        }

        td {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }

        tr:hover {
            background: #f2f7ff;
        }

        /* Buttons inside tables */
        .btn {
            padding: 6px 10px;
            border-radius: 5px;
            text-decoration: none;
            font-size: 14px;
            color: white;
        }
        .btn-edit {
            background: #28a745;
        }
        .btn-delete {
            background: #e63946;
        }
        .btn-export {
            background: #f4a261;
            margin-top: 10px;
        }

        .btn:hover {
            opacity: 0.85;
        }

        /* Links */
        a {
            text-decoration: none;
            color: #2575fc;
        }

        /* Title Section */
        header {
            text-align: center;
            padding: 20px;
            color: white;
        }
        header h1 {
            font-size: 28px;
        }
    </style>
</head>
<body>
<header>
    <h1>💰 Finance Tracker</h1>
</header>

{% if page == 'login' %}
    <div class="container">
        <h2>Login</h2>
        <form method="POST" action="/">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Login</button>
        </form>
        <p>Don't have an account? <a href="/register">Register</a></p>
    </div>

{% elif page == 'register' %}
    <div class="container">
        <h2>Register</h2>
        <form method="POST" action="/register">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Register</button>
        </form>
        <p><a href="/">Back to Login</a></p>
    </div>

{% elif page == 'dashboard' %}
    <h2 style="color:white;">Welcome, {{ username }}</h2>
    <div class="menu">
        <a href="/add">➕ Add</a>
        <a href="/transactions">📄 View</a>
        <a href="/summary">📊 Summary</a>
        <a href="/logout">🚪 Logout</a>
    </div>

{% elif page == 'add' %}
    <div class="container">
        <h2>Add Transaction</h2>
        <form method="POST">
            <select name="type" required>
                <option value="income">Income</option>
                <option value="expense">Expense</option>
            </select><br>
            <input type="number" name="amount" placeholder="Amount" step="0.01" required><br>
            <input type="text" name="category" placeholder="Category"><br>
            <input type="text" name="description" placeholder="Description"><br>
            <input type="date" name="date" required><br>
            <button type="submit">Add Transaction</button>
        </form>
        <p><a href="/dashboard">Back to Dashboard</a></p>
    </div>

{% elif page == 'transactions' %}
    <h2 style="color:white;">Your Transactions</h2>
    <form method="GET" action="/transactions" style="margin-bottom:20px;">
        <input type="text" name="search" placeholder="Search category or description">
        <input type="date" name="start_date">
        <input type="date" name="end_date">
        <button type="submit">Search</button>
        <a class="btn btn-export" href="/export">Export CSV</a>
    </form>
    <table>
        <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Amount</th>
            <th>Category</th>
            <th>Description</th>
            <th>Date</th>
            <th>Actions</th>
        </tr>
        {% for t in transactions %}
        <tr>
            <td>{{ t.id }}</td>
            <td>{{ t.type }}</td>
            <td>₹{{ t.amount }}</td>
            <td>{{ t.category }}</td>
            <td>{{ t.description }}</td>
            <td>{{ t.date }}</td>
            <td>
                <a class="btn btn-edit" href="/edit/{{ t.id }}">Edit</a>
                <a class="btn btn-delete" href="/delete/{{ t.id }}">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </table>
    <p><a href="/dashboard" style="color:white;">Back to Dashboard</a></p>

{% elif page == 'edit' %}
    <div class="container">
        <h2>Edit Transaction</h2>
        <form method="POST">
            <select name="type" required>
                <option value="income" {% if transaction.type == 'income' %}selected{% endif %}>Income</option>
                <option value="expense" {% if transaction.type == 'expense' %}selected{% endif %}>Expense</option>
            </select><br>
            <input type="number" name="amount" value="{{ transaction.amount }}" step="0.01" required><br>
            <input type="text" name="category" value="{{ transaction.category }}"><br>
            <input type="text" name="description" value="{{ transaction.description }}"><br>
            <input type="date" name="date" value="{{ transaction.date }}" required><br>
            <button type="submit">Update</button>
        </form>
        <p><a href="/transactions">Back to Transactions</a></p>
    </div>

{% elif page == 'summary' %}
    <div class="container">
        <h2>Summary for {{ year }}-{{ month }}</h2>
        <form method="POST">
            <input type="month" name="month" required>
            <button type="submit">View</button>
        </form>
        <p><strong>Income:</strong> ₹{{ income }}</p>
        <p><strong>Expense:</strong> ₹{{ expense }}</p>
        <p><strong>Balance:</strong> ₹{{ balance }}</p>
        <p><a href="/dashboard">Back to Dashboard</a></p>
    </div>

{% endif %}
</body>
</html>
"""

# ------------------ Routes ------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])
        db = connect_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            return "<h3 style='color:white;text-align:center;'>Invalid login</h3><p style='text-align:center;'><a href='/'>Try again</a></p>"
    return render_template_string(HTML_TEMPLATE, page="login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])
        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            return "<h3>Registered Successfully!</h3><a href='/'>Login Here</a>"
        except mysql.connector.IntegrityError:
            return "<h3>Username already exists!</h3><a href='/register'>Try again</a>"
        finally:
            cursor.close()
            db.close()
    return render_template_string(HTML_TEMPLATE, page="register")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template_string(HTML_TEMPLATE, page="dashboard", username=session["username"])

@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        t_type = request.form["type"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        description = request.form["description"]
        date = request.form["date"]
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, type, amount, category, description, date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session["user_id"], t_type, amount, category, description, date))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("transactions"))
    return render_template_string(HTML_TEMPLATE, page="add")

@app.route("/transactions")
def transactions():
    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    query = "SELECT * FROM transactions WHERE user_id=%s"
    params = [session["user_id"]]

    if search:
        query += " AND (category LIKE %s OR description LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    if start_date:
        query += " AND date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND date <= %s"
        params.append(end_date)

    query += " ORDER BY date DESC"

    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template_string(HTML_TEMPLATE, page="transactions", transactions=data)

@app.route("/edit/<int:txn_id>", methods=["GET", "POST"])
def edit_transaction(txn_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = connect_db()
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        t_type = request.form["type"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        description = request.form["description"]
        date = request.form["date"]
        cursor.execute("""
            UPDATE transactions SET type=%s, amount=%s, category=%s, description=%s, date=%s
            WHERE id=%s AND user_id=%s
        """, (t_type, amount, category, description, date, txn_id, session["user_id"]))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("transactions"))
    else:
        cursor.execute("SELECT * FROM transactions WHERE id=%s AND user_id=%s", (txn_id, session["user_id"]))
        transaction = cursor.fetchone()
        cursor.close()
        db.close()
        return render_template_string(HTML_TEMPLATE, page="edit", transaction=transaction)

@app.route("/delete/<int:txn_id>")
def delete_transaction(txn_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=%s AND user_id=%s", (txn_id, session["user_id"]))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for("transactions"))

@app.route("/export")
def export_csv():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions WHERE user_id=%s ORDER BY date DESC", (session["user_id"],))
    data = cursor.fetchall()
    cursor.close()
    db.close()

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv",
                     as_attachment=True, download_name="transactions.csv")

@app.route("/summary", methods=["GET", "POST"])
def summary():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        month = request.form["month"]
        year, mon = map(int, month.split("-"))
    else:
        today = datetime.today()
        year, mon = today.year, today.month

    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT type, SUM(amount) FROM transactions
        WHERE user_id=%s AND YEAR(date)=%s AND MONTH(date)=%s
        GROUP BY type
    """, (session["user_id"], year, mon))
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
    return render_template_string(HTML_TEMPLATE, page="summary", year=year, month=mon,
                                  income=income, expense=expense, balance=balance)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
