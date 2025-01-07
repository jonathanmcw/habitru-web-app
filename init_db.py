import sqlite3

def init_db():
    conn = sqlite3.connect('habitru.db')
    c = conn.cursor()

    # Create table
    c.execute('''
        CREATE TABLE IF NOT EXISTS habits (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              type TEXT NOT NULL,
              value TEXT NOT NULL,
              done INTEGER DEFAULT 0,
              description TEXT
        )          
    ''')

    habits = [
        ('Wake up', 'at_time', '7am', 0, 'Wake up early in the morning'),
        ('Work out', 'for_time', '60mins', 0, 'Daily workout routine'),
        ('Boil Eggs Breakfast', 'for_qty', '4', 0, 'Maintain a healthy diet')
    ]
    c.executemany('INSERT INTO habits (name, type, value, done, description) VALUES (?,?,?,?,?)', habits)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    