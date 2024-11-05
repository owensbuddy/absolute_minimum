import sqlite3

# Path to the database
db_path = '/Users/buddy/Desktop/School/effective-adventure/effective-adventure/db/WGU_Reddit.db'

# Connect to the database
print(f"Connecting to SQLite database at {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
print("Database connection established.")

# Clear the existing 'comments_new' table if it exists
try:
    cursor.execute('DROP TABLE IF EXISTS comments_new')
    print("Cleared existing 'comments_new' table.")
except sqlite3.OperationalError as e:
    print(f"Error dropping 'comments_new' table: {e}")

# Create a new 'comments_new' table with the correct structure
try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id TEXT UNIQUE,
            post_id TEXT,
            parent_id TEXT,
            author TEXT,
            content TEXT,
            upvotes INTEGER,
            created_utc REAL,
            ratio REAL
        )
    ''')
    print("Created 'comments_new' table with the correct structure.")
except sqlite3.OperationalError as e:
    print(f"Error creating 'comments_new' table: {e}")

# Optional: Transfer existing data from 'comments' to 'comments_new'
# Uncomment the following code block if you want to transfer data
# print("Transferring data from 'comments' to 'comments_new'...")
# cursor.execute('''
#     INSERT INTO comments_new (comment_id, post_id, author, content, upvotes, created_utc, ratio)
#     SELECT comment_id, post_id, author, content, upvotes, created_utc, ratio FROM comments
# ''')
# print("Data transferred to 'comments_new' table.")

# Commit the changes
conn.commit()
print("Changes committed.")

# Optional: Rename tables if you want 'comments_new' to replace 'comments'
# Be cautious with this step and ensure you have backups if necessary
# cursor.execute("ALTER TABLE comments RENAME TO comments_old")
# cursor.execute("ALTER TABLE comments_new RENAME TO comments")
# print("Renamed 'comments_new' table to 'comments'.")

# Close the database connection
conn.close()
print("Database connection closed.")