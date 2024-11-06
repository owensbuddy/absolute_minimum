import sys
import os
import sqlite3
import praw

# Load Reddit credentials from config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../config')))
from config import REDDIT_CREDENTIALS

# Initialize Reddit instance
reddit = praw.Reddit(
    client_id=REDDIT_CREDENTIALS['client_id'],
    client_secret=REDDIT_CREDENTIALS['client_secret'],
    user_agent=REDDIT_CREDENTIALS['user_agent']
)

def fetch_and_update_subreddit_data(db_path='/Users/buddy/Desktop/School/effective-adventure/effective-adventure/db/WGU_Reddit.db'):
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure the 'subreddits' table exists with the correct schema
    create_subreddits_table_sql = '''
    CREATE TABLE IF NOT EXISTS subreddits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subreddit TEXT UNIQUE,
        subreddit_id TEXT,
        title TEXT,
        description TEXT,
        url TEXT,
        created_utc REAL,
        subscriber_count INTEGER,
        active_user_count INTEGER,
        num_posts INTEGER DEFAULT 0
    )
    '''
    cursor.execute(create_subreddits_table_sql)

    # Retrieve unique subreddits from the 'posts' table
    cursor.execute("SELECT DISTINCT subreddit FROM posts WHERE subreddit IS NOT NULL")
    subreddits_in_posts = [row[0] for row in cursor.fetchall()]

    for subreddit_name in subreddits_in_posts:
        print(f"Fetching data for subreddit: {subreddit_name}")
        try:
            # Fetch subreddit data from Reddit
            subreddit = reddit.subreddit(subreddit_name)
            subreddit_data = {
                "subreddit": subreddit.display_name,
                "subreddit_id": subreddit.id,
                "title": subreddit.title,
                "description": subreddit.public_description,
                "url": subreddit.url,
                "created_utc": subreddit.created_utc,
                "subscriber_count": subreddit.subscribers,
                "active_user_count": subreddit.active_user_count,
            }

            # Count posts for the subreddit in the 'posts' table
            cursor.execute("SELECT COUNT(*) FROM posts WHERE subreddit = ?", (subreddit_name,))
            post_count = cursor.fetchone()[0]
            subreddit_data["num_posts"] = post_count

            # Insert or update subreddit data in the 'subreddits' table
            insert_sql = '''
            INSERT INTO subreddits (subreddit, subreddit_id, title, description, url, created_utc, subscriber_count, active_user_count, num_posts)
            VALUES (:subreddit, :subreddit_id, :title, :description, :url, :created_utc, :subscriber_count, :active_user_count, :num_posts)
            ON CONFLICT(subreddit) DO UPDATE SET 
                subreddit_id = excluded.subreddit_id,
                title = excluded.title,
                description = excluded.description,
                url = excluded.url,
                created_utc = excluded.created_utc,
                subscriber_count = excluded.subscriber_count,
                active_user_count = excluded.active_user_count,
                num_posts = excluded.num_posts
            '''
            cursor.execute(insert_sql, subreddit_data)
            print(f"Updated '{subreddit_name}' with {post_count} posts.")

        except Exception as e:
            print(f"Error fetching data for '{subreddit_name}': {e}")

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Subreddit data updated in the database.")

if __name__ == "__main__":
    fetch_and_update_subreddit_data()