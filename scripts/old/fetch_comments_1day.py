import sys
import os
import praw
import sqlite3
import datetime
from datetime import timedelta
import json

# Timeframe for fetching comments (in days)
TIMEFRAME_DAYS = 1

# Path to the config file
config_path = '/Users/buddy/Desktop/School/effective-adventure/effective-adventure/config/config.py'

# Settings
TEST_MODE = True  # Set to True to fetch only the first comment per post for testing

# Load the config using exec()
config = {}
print("Loading configuration...")
with open(config_path, 'r') as file:
    exec(file.read(), config)
print("Configuration loaded successfully.")

# Initialize Reddit instance with credentials from config
print("Initializing Reddit instance...")
reddit = praw.Reddit(
    client_id=config['REDDIT_CREDENTIALS']['client_id'],
    client_secret=config['REDDIT_CREDENTIALS']['client_secret'],
    user_agent=config['REDDIT_CREDENTIALS']['user_agent']
)
print("Reddit instance initialized.")

# Connect to SQLite database
db_path = '/Users/buddy/Desktop/School/effective-adventure/effective-adventure/db/WGU_Reddit.db'
print(f"Connecting to SQLite database at {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
print("Database connection established.")

# Define function to insert a comment into the database
def insert_comment(comment_data):
    cursor.execute('''
        INSERT OR IGNORE INTO comments (comment_id, post_id, author, content, upvotes, created_utc)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        comment_data['id'],
        comment_data['post_id'],
        comment_data['author'],
        comment_data['content'],
        comment_data['upvotes'],
        comment_data['created_utc']
    ))

# Calculate the start time for fetching comments
fetch_start_time = datetime.datetime.utcnow() - timedelta(days=TIMEFRAME_DAYS)
print(f"Fetching comments from the last {TIMEFRAME_DAYS} days...")

# Fetch posts that already have comments within the specified timeframe
cursor.execute('''
    SELECT post_id FROM posts 
    WHERE EXISTS (
        SELECT 1 FROM comments WHERE comments.post_id = posts.post_id
    ) AND created_utc >= ?
''', (fetch_start_time.timestamp(),))
recent_posts = cursor.fetchall()

total_comments_added = 0
post_count = 0
update_interval = 10  # Adjust for desired progress updates
all_recent_comments = []

for (post_id,) in recent_posts:
    post = reddit.submission(id=post_id)
    post.comment_sort = 'new'
    post.comments.replace_more(limit=None)

    post_comments = []
    for comment in post.comments.list():
        comment_time = datetime.datetime.utcfromtimestamp(comment.created_utc)
        if comment_time < fetch_start_time:
            continue

        comment_data = {
            'id': comment.id,
            'post_id': post_id,
            'author': comment.author.name if comment.author else None,
            'content': comment.body,
            'upvotes': comment.score,
            'created_utc': comment.created_utc
        }

        insert_comment(comment_data)
        post_comments.append(comment_data)
        total_comments_added += 1

    # Commit the transaction after processing each post
    conn.commit()
    post_count += 1

    # Update the last_comment_fetch timestamp for the post if comments were added
    if post_comments:
        cursor.execute('UPDATE posts SET last_comment_fetch = ? WHERE post_id = ?', 
                       (datetime.datetime.utcnow().timestamp(), post_id))
        all_recent_comments.append({'post_id': post_id, 'comments': post_comments})

    # Print progress update every `update_interval` posts
    if post_count % update_interval == 0:
        print(f"Processed {post_count} posts, {total_comments_added} comments added so far...")

# Save all posts with their comments to a JSON file
output_path = '/Users/buddy/Desktop/School/effective-adventure/effective-adventure/data/recent_comments.json'
with open(output_path, 'w') as f:
    json.dump(all_recent_comments, f, indent=4)

# Close the database connection
conn.close()
print("Database connection closed.")
print(f"Summary: {total_comments_added} comments added or updated.")