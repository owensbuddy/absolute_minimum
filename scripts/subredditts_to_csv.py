import sqlite3
import csv
import pandas as pd
from datetime import datetime

# Connect to the SQLite database
db_path = '/Users/buddy/Desktop/School/effective-adventure/effective-adventure/db/WGU_Reddit.db'
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Query to select all data from the subreddits table
query = "SELECT * FROM subreddits"
cursor.execute(query)

# Fetch all rows from the executed query
rows = cursor.fetchall()

# Fetch column names from the cursor
column_names = [description[0] for description in cursor.description]

# Convert fetched data into a DataFrame
df = pd.DataFrame(rows, columns=column_names)

# Debug: print column names
print("Column names in the DataFrame:", df.columns.tolist())

# Convert 'created_utc' from timestamp to datetime and calculate age
df['created_utc'] = pd.to_datetime(df['created_utc'], unit='s')
current_date = datetime.now()
df['Age (y)'] = ((current_date - df['created_utc']).dt.days / 365).round(1)

# ## Data Cleaning

# Drop the specified columns if they exist
columns_to_drop = ['id', 'subreddit_id', 'url', 'active_user_count', 'created_utc']  # Adjust if needed
df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

# Rename the subscriber_count column to Subscribers
df.rename(columns={'subscriber_count': 'Subscribers'}, inplace=True)

# Replace newlines in the descriptions with spaces or a placeholder
if 'description' in df.columns:
    df['description'] = df['description'].str.replace('\n', ' ', regex=False)  # Replace line breaks with spaces

# Define the CSV file path
csv_file_path = '/Users/buddy/Desktop/School/effective-adventure/effective-adventure/data/subreddits.csv'

# Write the cleaned DataFrame to CSV without the index
df.to_csv(csv_file_path, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)

# Close the database connection
connection.close()

print(f"Data successfully extracted and cleaned to {csv_file_path}")