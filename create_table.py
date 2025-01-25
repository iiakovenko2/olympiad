import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/olympiad.db')
cursor = conn.cursor()

# Create the results table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        answers TEXT
    )
''')

# Commit and close the connection
conn.commit()
conn.close()

print("Results table created successfully.")
