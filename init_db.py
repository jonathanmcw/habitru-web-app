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
              value TEXT NOT NULL
        )          
    ''')

    habits = [
        ('Wake up', 'at_time', '7am'),
        ('Work out', 'for_time', '60mins'),
        ('Boil Eggs Breakfast', 'for_qty', '4')
    ]
    c.executemany('INSERT INTO habits (name, type, value) VALUES (?,?,?)', habits)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    
