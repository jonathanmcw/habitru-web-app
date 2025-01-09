from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

# To do:
# Root 
# > "what habit or activities would you like to tracK?" 
#       [ ] need to have couple more options - time to ask around to brainstorm
#       [ ] Idea: keep a notebook myself to see what kind of things can / should be quantified
#       [NEXT] Both Physical, Emotional, Social
# > Home screen
#       [ ] Show only habit that are not done today
#       [ ] Go to next date 
#       [ ] ?? Mark a task back to "not done?"
#       [DONE] Keep it very simple with as little fiddling as possible.
#           [DONE] Click to mark item as done
#           [NEXT] Long press to mark something not done done
#           [DONE] Tap into item for details
#           [NEXT] Tactile - like a bubble sheet + sound
#       [DONE] Button row to add new item 
#           [DONE] Name
#           [NEXT] Description
#           [NEXT] Quantity / Unit ( affects the type of UI to be generated )
#           [DONE] Frequency / start / end date 
#           [NEXT] end date
#       
# > monthly-view screen
#       [NEXT] - Emotionally, make it very satisfying to look at :) like a proper achievement
#       [NEXT] My stats and streaks :) 
#           - any sort of insights I could dig from there
# > Year screen
#       [ ] Convert date into 365 and then show
#       [ ] Show done item for the year 
# > Profile
#       [LATER] Consider what are the needs, and whether we do need to have a family account to share success
# > Why people procrastinate ? 

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
    conn.close()
    print("Fetched habits:", habits)  # Debug print statement
    return render_template('welcome.html', habits=habits, current_url=request.path)

@app.route("/daily_view", methods=["GET","POST"])
def daily_view():

    # TODO: Enable user to switch day 
    # TODO: How should I design my database to have task of different dates? 
    current_time = datetime.now().strftime("%-d %b %Y")

    if request.method == "POST":
        conn = get_db_connection()

        # ??? how do I render the daily, monthly and yearly list?
        # ??? daily - SELECT * FROM records or progress (???) WHERE values is zero ? 
        # ??? NOTE: Method 2 >>> Where today needs to do something but record shows not found ... >>> just join table 
        #    
        # TODO:
        # habit_id = request.form.get("habit-id")
        # conn.execute("UPDATE ")
        # conn.execute("INSERT INTO records (habit_id, done) VALUES (?, ?) ", habit_id ,1)
            # return render_template('daily_view.html', habits = habits, current_time = current_time, current_url=request.path )
        
        # <p>Current version: type: "to_do" value: "none" start_date: "today", frequency: "daily"</p>

        # COULD BE ADDING NEW
        habit_name = request.form.get("habit-name")
        # TODO: validation
        conn.execute("INSERT INTO habits (name, type, value, description, start_date, frequency) VALUES (?, ?, ?, ?, ?, ?)", (habit_name, "to_do", "none", "empty", "2025-01-09", "daily"))
        conn.commit()
        conn.close()

        return redirect(url_for('daily_view'))
    
    conn = get_db_connection()

    habits = conn.execute('SELECT * FROM habits').fetchall()
    conn.close()
    return render_template('daily_view.html', habits = habits, current_time = current_time, current_url=request.path )

# Update / Add view

@app.route("/monthly_view")
def monthly_view():
    current_time = datetime.now().strftime("%b %Y")

    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits').fetchall()
    conn.close()
    
    dates = []
    months = []

    return render_template('monthly_view.html', habits=habits, current_time = current_time, dates=dates, months = months, current_url=request.path)
    # return render_template('monthly-view.html', transposed_data=transposed_data, habits=habits, dates=dates)


@app.route("/yearly_view")
def yearly_view():
    current_time = datetime.now().strftime("%Y")

    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits').fetchall()
    habit_records = conn.execute('''SELECT records.date, records.habit_id, habits.name FROM records 
                                    JOIN habits ON records.habit_id = habits.id 
                                    WHERE date LIKE '2025%'  
                                    ORDER BY habits.id''').fetchall()
    conn.close()

    def date_to_day_of_year(date_str):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.timetuple().tm_yday

    habit_records = [{"day_of_year": date_to_day_of_year(record["date"]), 
                      "habit_id": record["habit_id"], 
                      "name": record["name"]} for record in habit_records]
    
    return render_template('yearly_view.html', current_time=current_time, habits=habits, habit_records=habit_records, current_url=request.path)

@app.route("/habit_details", methods=["GET"])
def habit_details():    
    habit_id = request.args.get("id")

    conn = get_db_connection()
    habit_row = conn.execute("SELECT * FROM habits WHERE id = ?;", habit_id).fetchone()
    conn.close()

    habit_info = {}

    if habit_row:
        habit_info["id"] = habit_row["id"]
        habit_info["habit_name"] = habit_row["name"]
        habit_info["type"] = habit_row["type"]
        habit_info["value"] = habit_row["value"]

    return render_template('habit_details.html', habit_info=habit_info)

@app.route("/new_habit")
def new_habit():
    return render_template('new_habit.html')

@app.route("/mark_done/<int:habit_id>", methods=["POST"])
def mark_done(habit_id):
    conn = get_db_connection()
    # conn.execute('UPDATE habits SET done = 1 WHERE id = ?;', (habit_id,))
    conn.execute('INSERT INTO records (habit_id, date, status) VALUES (?, "2025-01-09", "done");', (habit_id,))
    conn.commit()
    conn.close()
    return '', 204 # No content

if __name__ == "__main__":
    app.run(debug=True)