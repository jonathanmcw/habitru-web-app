from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Ensure no caching
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def get_db_connection():
    conn = sqlite3.connect('habitru.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def welcome():
    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits').fetchall()
    # habits = [
    #     {'name': 'wake-up', 'label': 'Wake up', 'value': 'wake-up',},
    #     {'name': 'workout', 'label': 'Workout', 'value': 'workout',},
    #     {'name': 'diet', 'label': 'Diet', 'value': 'diet',}
    # ]
    return render_template('welcome.html', habits = habits)
    # return "<html><body>what exercise would you like to track?</body></html>"

@app.route("/home", methods=["GET","POST"])
def home():
    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits').fetchall()
    conn.close()
    # habits = [
    #         {'name': 'wake-up', 'label': 'Wake up', 'value': 'wake-up',},
    #         {'name': 'workout', 'label': 'Workout', 'value': 'workout',},
    #         {'name': 'diet', 'label': 'Diet', 'value': 'diet',}
    #     ]
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if request.method == "POST":
        return redirect(url_for('home'))
    return render_template('home.html', habits = habits, current_time = current_time )

@app.route("/summary")
def summary():
    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits').fetchall()
    dates = [f"2025-01-{i+1:02d}" for i in range(30)]
    conn.close()
    return render_template('summary.html', habits=habits, dates=dates)

@app.route("/profile")
def profile():
    return render_template('profile.html')

if __name__ == "__main__":
    app.run(debug=True)