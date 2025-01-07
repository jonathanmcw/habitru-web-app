from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

# To do:
# Root 
# > "what habit or activities would you like to tracK?" 
#       [ ] need to have couple more options - time to ask around to brainstorm
#       [ ] Idea: keep a notebook myself to see what kind of things can / should be quantified
#       [ ] Both Physical, Emotional, Social
# > Home screen
#       [ ] Keep it very simple with as little fiddling as possible.
#           - Click to mark item as done
#           - Long press to mark something not done done
#           - Tap into item for details
#           - Tactile - like a bubble sheet + sound
#       [ ] Button row to add new item 
#           - Name
#           - Description
#           - Quantity / Unit ( affects the type of UI to be generated )
#           - Frequency / start / end date
# > monthly-view screen
#       [ ] - Emotionally, make it very satisfying to look at :) like a proper achievement
#       [ ] My stats and streaks :) 
#           - any sort of insights I could dig from there
# > Profile
#       [ ] Consider what are the needs, and whether we do need to have a family account to share success
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

    # TODO: Based on what the option that I have selected, the options should be shown to be in Today

    # habits = [
    #     {'name': 'wake-up', 'label': 'Wake up', 'value': 'wake-up',},
    #     {'name': 'workout', 'label': 'Workout', 'value': 'workout',},
    #     {'name': 'diet', 'label': 'Diet', 'value': 'diet',}
    # ]
    return render_template('welcome.html', habits = habits)
    # return "<html><body>what exercise would you like to track?</body></html>"

@app.route("/daily_view", methods=["GET","POST"])
def daily_view():
    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits').fetchall()
    conn.close()
    # habits = [
    #         {'name': 'wake-up', 'label': 'Wake up', 'value': 'wake-up',},
    #         {'name': 'workout', 'label': 'Workout', 'value': 'workout',},
    #         {'name': 'diet', 'label': 'Diet', 'value': 'diet',}
    #     ]
    # TODO: Enable user to switch day 
    # TODO: How should I design my database to have task of different dates? 
    current_time = datetime.now().strftime("%-d %b %Y")
    if request.method == "POST":
        return redirect(url_for('daily_view'))
    return render_template('daily_view.html', habits = habits, current_time = current_time )

# Update / Add view

@app.route("/monthly_view")
def monthly_view():
    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits').fetchall()
    conn.close()
    
    # dates = [f"2025-01-{i+1:02d}" for i in range(30)]
    dates = [f"{i+1:02d}" for i in range(30)]
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    # dates.reverse()

    # transposed_data = []
    # for i in range(30):
    #     row = {'date': dates[i], 'habits': []}
    #     for habit in habits:
    #         row['habits'].append(habit)
    #     transposed_data.append(row)

    return render_template('monthly_view.html', habits=habits, dates=dates, months = months)
    # return render_template('monthly-view.html', transposed_data=transposed_data, habits=habits, dates=dates)


@app.route("/profile")
def profile():
    return render_template('profile.html')

@app.route("/mark_done/<int:habit_id>", methods=["POST"])
def mark_done(habit_id):
    conn = get_db_connection()
    conn.execute('UPDATE habits SET done = 1 WHERE id = ?', (habit_id,))
    conn.commit()
    conn.close()
    return '', 204 # No content


if __name__ == "__main__":
    app.run(debug=True)