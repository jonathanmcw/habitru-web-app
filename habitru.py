from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import re
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# To do:
# Root 
# > "what habit or activities would you like to tracK?" 
#       [ ] need to have couple more options - time to ask around to brainstorm
#       [ ] Idea: keep a notebook myself to see what kind of things can / should be quantified
#       [NEXT] Both Physical, Emotional, Social
# > Home screen
#       [DONE] Show only habit that are not done today
#       [ ] Go to next date
#           [DONE] Can navigate to any date with URL
#           [ ] Have date navigation
#       [DONE] Mark a task back to "not done?"
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
#       [Done] Convert date into 365 and then show
#       [Done] Show done item for the year 
# > Profile
#       [LATER] Consider what are the needs, and whether we do need to have a family account to share success
# > Why people procrastinate ? 

def create_date_object(year=None, month=None, day=None):
    now = datetime.now()

    if year is None:
        year = now.year
    
    if month is None or day is None:
        # year = now.year / To improve later
        month = now.month
        day = now.day
        
    date = {
        "current": {
            "date": now.strftime("%Y/%m/%d"),
            "year": now.strftime("%Y"),
            "month": now.strftime("%m"),
            "day": now.strftime("%d")
        },
        "selected": {
            "date": f"{year:04}/{month:02}/{day:02}",
            "year": f"{year:04}",
            "month": f"{month:02}",
            "day": f"{day:02}",
        },
        "db_format": {
            "date": f"{year:04}-{month:02}-{day:02}",
            "year": f"{year:04}%"
        }
    }
    return date

# Ensure no caching
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def get_db_connection():
    try:
        conn = sqlite3.connect('habitru.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

# Home - Simply show date of today
@app.route("/", defaults={"year": None, "month": None, "day": None}, methods=["GET", "POST"])
@app.route("/<int:year>/<int:month>/<int:day>/", methods=["GET","POST"])
def daily_view(year,month,day):

    date = create_date_object(year, month, day)
    conn = get_db_connection()

    if conn:
        habits = conn.execute('''   
            SELECT * FROM habits 
            LEFT JOIN records ON habits.id = records.habit_id
                AND records.date = ? AND records.status = 'done'
            WHERE records.habit_id IS NULL
            ''', (date["db_format"]["date"],)).fetchall()
        conn.close()
        return render_template('daily_view.html', habits=habits, date=date, current_url=request.path)
    else:
        flash("Database connection error.")
        return render_template('daily_view.html', habits=[], date=date, current_url=request.path)

# Year view
@app.route("/<int:year>/")
def yearly_view(year):

    date = create_date_object(year)
    conn = get_db_connection()

    if conn:
        habits = conn.execute('SELECT * FROM habits').fetchall()
        # year_to_search = f'{date["selected"]["year"]}%'
        habit_records = conn.execute('''SELECT records.date, records.habit_id, habits.name FROM records 
                                        JOIN habits ON records.habit_id = habits.id 
                                        WHERE date LIKE ?  
                                        ORDER BY habits.id''', (date["db_format"]["year"],)).fetchall()
        conn.close()

        def date_to_day_of_year(date_str):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.timetuple().tm_yday

        habit_records = [{"day_of_year": date_to_day_of_year(record["date"]), 
                          "habit_id": record["habit_id"], 
                          "name": record["name"]} for record in habit_records]
        
        return render_template('yearly_view.html', date=date, habits=habits, habit_records=habit_records, current_url=request.path)
    else:
        flash("Database connection error.")
        return render_template('yearly_view.html', date=date, habits=[], habit_records=[], current_url=request.path)

# View habit details at a specific date
@app.route("/<year>/<month>/<day>/<int:habit_id>", methods=["GET","POST"])
def habit_details(year, month, day, habit_id ):    

    date = create_date_object(year, month, day)
    conn = get_db_connection()

    if conn:
        habit_row = conn.execute('''
            SELECT habits.*, records.status 
            FROM habits
            LEFT JOIN records ON records.habit_id = habits.id AND records.date = ?
            WHERE habits.id = ?  
            ''', (date["db_format"]["date"], habit_id)).fetchone()
        
        conn.close()
        habit = {}

        if habit_row:
            habit["id"] = habit_row["id"]
            habit["habit_name"] = habit_row["name"]
            habit["type"] = habit_row["type"]
            habit["value"] = habit_row["value"]
            habit["date"] = date["selected"]["date"] # Changed format 
            habit["status"] = habit_row["status"] if habit_row["status"] else "not started"
        return render_template('habit_details.html', habit=habit, date=date)
    
    else:
        flash("Database connection error.")
        return render_template('habit_details.html', habit={}, date={})

# Add new habit to TABLE "habits" 
# TODO: Should be /habit/new in the long run, with a list of current habits to review 
@app.route("/new_habit", methods=["GET","POST"])
def new_habit():

    date = create_date_object()

    # ADD new habit
    if request.method == "POST":
        habit_name = request.form.get("habit-name")
        if not habit_name:
            flash("Habit name is required.")
            return redirect(url_for('new_habit'))

        conn = get_db_connection()

        if conn:
            conn.execute("INSERT INTO habits (name, type, value, description, start_date, frequency) VALUES (?, ?, ?, ?, ?, ?)", 
                         (habit_name, "to_do", "none", "empty", date["db_format"]["date"], "daily_view"))
            conn.commit()
            conn.close()
            return redirect(url_for('daily_view', year= date["selected"]["year"],  month= date["selected"]["month"],  day= date["selected"]["day"]))
        else:
            flash("Database connection error.")
            return redirect(request.referrer or url_for('daily_view'))
    
    # Present new habit input form 
    return render_template('new_habit.html')

# Update details of a habit, works with TABLE "habits"
@app.route("/habit/<int:habit_id>/update", methods=["GET", "POST"])
def update_habit(habit_id):
    action = request.form.get("action")
    habit_name = request.form.get("habit-name")
    # referrer = request.form.get("referrer")

    year = request.form.get("year")
    month = request.form.get("month")
    day = request.form.get("day")

    date = create_date_object(year, month, day)

    conn = get_db_connection()
    if conn:
        if request.method == "POST":
            if action == "save":
                if not habit_name:
                    return redirect(url_for('update_habit', habit_id=habit_id))
                
                conn.execute("UPDATE habits SET name = ? WHERE id = ?", (habit_name, habit_id))
                conn.commit()
                flash("Habit update successfully.")
                conn.close()
                return redirect(url_for('daily_view'))
            
            elif action == "delete":
                conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
                conn.execute("DELETE FROM records WHERE habit_id = ?", (habit_id,))
                conn.commit()
                flash("Habit deleted successfully")
                conn.close()
                return redirect(url_for('daily_view'))
            
        else:
            # Should be the editing form
            habit_row = conn.execute("SELECT * FROM habits WHERE id = ?;", (habit_id,)).fetchone()
            conn.close()

            habit = {}
            if habit_row:
                # column_names = [desc[0] for dsec in cursor.description]
                for key in habit_row.keys():
                    habit[key] = habit_row[key]

            return render_template('edit_habit.html', habit=habit, date=date)
    else:
        flash("Database connection error.")
        return redirect(url_for('daily_view'))


# Update progress of a habit (task) at a date, works with TABLE "records"
# Done via async - Should it be "/yyyy/mm/dd/id/update" ?
@app.route("/update_status", methods=["POST"])
def update_status():
    habit_id = request.form.get("id")
    task_date = request.form.get("date").replace("/", "-")
    referrer = request.form.get("referrer")
    
    conn = get_db_connection()
    if conn:
        # Check if the task is already marked as done
        record = conn.execute('''SELECT * FROM records
                                WHERE habit_id = ? AND date = ? AND status = "done";''',
                                (habit_id, task_date)).fetchone()
        
        if record:
            # If the task is 'done', delete the record to mark it as not done
            conn.execute('''DELETE FROM records
                            WHERE habit_id = ? AND date = ? AND status = "done";''',
                            (habit_id, task_date))
            
        else:
            # If the task is not done, insert a new record to mark it as done 
            conn.execute('''INSERT INTO records (habit_id, date, status) 
                            VALUES (?, ?, "done");''', (habit_id, task_date))
        conn.commit()
        conn.close()
        return redirect(referrer or url_for('daily_view'))
    else:
        flash("Database connection error.")
        return redirect(referrer or url_for('daily_view')) 

if __name__ == "__main__":
    app.run(debug=True)