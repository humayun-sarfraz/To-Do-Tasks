from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Get the base directory of the application 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")  # Path to the database folder
DB_PATH = os.path.join(DB_DIR, "tasks.db")   # Path to the database file

# Create the database folder if it doesn't exist
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Create a connection to SQLite database
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Create tasks table if it does not exist
cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    created TEXT NOT NULL,
                    status TEXT NOT NULL)''')
conn.commit()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        task = request.form["task"]
        created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = "In Open Task"  # Default status when adding new task
        # Insert new task into the tasks table
        cursor.execute("INSERT INTO tasks (task, created, status) VALUES (?, ?, ?)", (task, created, status))
        conn.commit()
        return redirect(url_for("index"))
    
    # Fetch all tasks from the database
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    
    # Create a list of dictionaries for tasks
    task_list = []
    for row in tasks:
        task_dict = {
            "id": row[0],
            "task": row[1],
            "created": row[2],
            "status": row[3]
        }
        task_list.append(task_dict)
    
    return render_template("index.html", tasks=task_list)

@app.route("/update_status/<int:task_id>", methods=["POST"])
def update_status(task_id):
    new_status = request.form["status"]
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete(task_id):
    # Delete the task from the database
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    return redirect(url_for("index"))

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    if request.method == "POST":
        new_task = request.form["task"]
        # Update the task in the database
        cursor.execute("UPDATE tasks SET task = ? WHERE id = ?", (new_task, task_id))
        conn.commit()
        return redirect(url_for("index"))
    
    # Fetch the task to be edited from the database
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    
    return render_template("edit.html", task=task)

if __name__ == "__main__":
    app.run(debug=True)
