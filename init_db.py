import sqlite3

def init_db():
    conn = sqlite3.connect('habitru.db')
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                value TEXT NOT NULL, 
                description TEXT,
                start_date DATE NOT NULL, 
                frequency TEXT DEFAULT 'daily'
            )          
        ''')
        print("Created table 'habits'")

        c.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                date DATE NOT NULL,
                status TEXT NOT NULL,
                progress_details TEXT,
                notes TEXT,
                FOREIGN KEY (habit_id) REFERENCES habits(id)
            )
        ''')
        print("Created table 'records'")

        habits = [
            ('Wake up at 7am', 'at_time', '7am', 'Wake up early in the morning', '2025-01-01','daily'),
            ('Work out 60mins', 'for_time', '60mins','Daily workout routine', '2025-01-01','daily'),
            ('4 Boil Eggs for Breakfast', 'for_qty', '4', 'Maintain a healthy diet', '2025-01-01','daily'),
            ('Writing for 30mins','for_time','30mins','De-clutter thinking for insights', '2025-01-01','daily'),
            ('Drink 8 glasses of water','for_qty','8','Stay hydrated','2025-01-01','daily')
        ]

        records = [
            (1, '2025-01-01', 'done', '', 'Woke up on time')
        ]

        c.executemany('INSERT INTO habits (name, type, value, description, start_date, frequency) VALUES (?,?,?,?,?,?)', habits)
        print("Inserted data into 'habits'")

        c.executemany('INSERT INTO records (habit_id, date, status, progress_details, notes) VALUES (?,?,?,?,?)', records)
        print("Inserted data into 'records'")

        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
