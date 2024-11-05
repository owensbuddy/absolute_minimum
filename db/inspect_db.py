import sqlite3

# Path to the database
db_path = '/Users/buddy/Desktop/School/effective-adventure/effective-adventure/db/WGU_Reddit.db'

print(f"Connecting to SQLite database at {db_path}...")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("Database connection established.")
except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")
    exit(1)

# Function to inspect database tables
def inspect_db():
    print("Inspecting database...")

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    if not tables:
        print("No tables found in the database.")
        return

    # Loop through each table to gather details
    for table_name in tables:
        table_name = table_name[0]
        print(f"\nTable: {table_name}")

        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        if columns_info:
            print("Columns:")
            for col in columns_info:
                print(f" - {col[1]} (Type: {col[2]})")
        else:
            print("No columns found.")

        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        print(f"Number of rows: {row_count}")

        # Get a sample of 5 rows
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        sample_data = cursor.fetchall()
       

# Run the inspection
inspect_db()

# Close the connection
conn.close()
print("Database connection closed.")