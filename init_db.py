import sqlite3

def init_db():
    conn = sqlite3.connect('habitru.db')
    c = conn.cursor()

    # Create table
    # c.execute('''
    #     CREATE TABLE IF NOT EXISTS habits (
    #           id INTEGER PRIMARY KEY AUTOINCREMENT,
    #           name TEXT NOT NULL,
    #           type TEXT NOT NULL,
    #           value TEXT NOT NULL,
    #           done INTEGER DEFAULT 0,
    #           description TEXT
    #     )          
    # ''')

    # c.execute(```
    #     CREATE TABLE IF NOT EXISTS habits (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name TEXT NOT NULL,
    #         tracking-method TEXT NOT NULL,
    #         tracking-value TEXT NOT NULL,
    #         tracking-frequency TEXT NOT NULL,
    #         tracking-details TEXT NOT NULL,
    #         start-date TEXT
    #     )          
    # ```)

    # c.execute(```
    #     CREATE TABLE IF NOT EXISTS record (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         date
    #         habits-id # foreign key from 
    #         status TEXT NOT NULL
    #         progress-details
    #         user-notes TEXT      
    #     )
    # ```)

    habits = [
        ('Wake up at 7am', 'at_time', '7am', 0, 'Wake up early in the morning'),
        ('Work out 60mins', 'for_time', '60mins', 0, 'Daily workout routine'),
        ('4 Boil Eggs for Breakfast', 'for_qty', '4', 0, 'Maintain a healthy diet')
    ]

# Scheme 
# HABITS
# - Habit Name - TEXT     
# - Type > Tracking method ( type of tracking ) - TEXT
# - Tracking value
# - START DATE
# - FREQUENCY
#   - DAILY 
#   - WEEKLY ( CUSTOM - SUN TO SAT ) 
#   - MONTHLY ( DATE 1 TO 30 )
#   ?? SPECIFIC DATE
#
# RECORD
# - ID
# - DATE - 2025-01-01
# - ACTIVITY ID ( Foreign ID )
# - STATUS - NOT STARTED / PROGRESS / DONE
# - PROGRESS DETAILS
#    - if Timer > 50m24s
#    - if Quantity > 5 times
#    - if Done or not done ... ( empty ) 
# - NOTES (?) 

# AMD / Google / AMAZON /
    c.executemany('INSERT INTO habits (name, type, value, done, description) VALUES (?,?,?,?,?)', habits)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    