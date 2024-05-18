import sqlite3

# Connect to the database

conn = sqlite3.connect('records.db')

# Create a cursor
c = conn.cursor()

# Create a table for security camera recording metadata
c.execute("""CREATE TABLE IF NOT EXISTS  meta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT,
    date_time TEXT
)""")

# Create a table to store the video file
c.execute('''CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    data BLOB NOT NULL
)''')
# Commit the command
conn.commit()

# Insert a record

# c.execute("INSERT INTO records VALUES (2, 'Vishnu', '2021-01-01')")
# conn.commit()

# insert a file

file_data = open('filename.avi', 'rb').read()
c.execute('''INSERT INTO files (name, data) VALUES (?, ?)''', ('filename.avi', file_data))
conn.commit()

# Access the records
data = c.execute("SELECT * FROM records").fetchall()
for row in data:
    print(row[0])

# Access File
# Select the file data from the database

# c.execute('''SELECT data FROM files WHERE name = ?''', ('filename.avi',))

# # Get the file data from the cursor object
# file_data = c.fetchone()[0]

# # Close the connection
# conn.close()

# # Write the file data to a new file
# with open('temp/filename.avi', 'wb') as f:
#     f.write(file_data)

# Close the connection
conn.close()