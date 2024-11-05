import sqlite3
import os

# Relative path to the database file
DB_PATH = './db/WGU_Reddit.db'

# SQL statements to create tables
TABLES = {
    "subreddits": """
        CREATE TABLE IF NOT EXISTS subreddits (
            id INTEGER PRIMARY KEY,
            subreddit TEXT UNIQUE,
            subreddit_id TEXT UNIQUE,
            title TEXT,
            description TEXT,
            url TEXT,
            created_utc REAL,
            subscriber_count INTEGER,
            active_user_count INTEGER
        );
    """,
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE
        );
    """,
    "posts": """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            post_id TEXT UNIQUE,
            subreddit TEXT,
            title TEXT,
            score INTEGER,
            author TEXT,
            created_utc REAL,
            num_comments INTEGER,
            selftext TEXT,
            url TEXT,
            permalink TEXT,
            FOREIGN KEY (subreddit) REFERENCES subreddits(subreddit),
            FOREIGN KEY (author) REFERENCES users(username)
        );
    """,
    "comments": """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            comment_id TEXT UNIQUE,
            post_id TEXT,
            author TEXT,
            content TEXT,
            upvotes INTEGER,
            created_utc REAL,
            FOREIGN KEY (post_id) REFERENCES posts(post_id),
            FOREIGN KEY (author) REFERENCES users(username)
        );
    """
}

# Ensure the db directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Connect to the database and create tables
def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for table_name, table_sql in TABLES.items():
            cursor.execute(table_sql)
        conn.commit()
    print("Database initialized with tables.")

if __name__ == '__main__':
    initialize_database()