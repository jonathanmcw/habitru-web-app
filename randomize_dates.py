import sqlite3
from datetime import datetime, timedelta
import random

def random_date(start, end):
    """Generate a random date between `start` and `end`."""
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def randomize_dates():
    conn = sqlite3.connect('habitru.db')
    try:
        c = conn.cursor()
        
        # Define the start and end dates
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)
        
        # Fetch all records
        records = c.execute('SELECT id FROM records').fetchall()
        
        # Update each record with a random date
        for record in records:
            record_id = record[0]
            new_date = random_date(start_date, end_date).strftime('%Y-%m-%d')
            c.execute('UPDATE records SET date = ? WHERE id = ?', (new_date, record_id))
        
        conn.commit()
        print("Dates randomized successfully.")
    finally:
        conn.close()

if __name__ == "__main__":
    randomize_dates()
