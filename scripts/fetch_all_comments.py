import sys
import os
import praw
import sqlite3
import json
import time
from datetime import datetime

# Path to the config file
config_path = '/Users/buddy/Desktop/School/effective-adventure/effective-adventure/config/config.py'

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

# Fetch posts that need comment fetching (where last_comment_fetch is NULL or outdated)
cursor.execute('''
    SELECT post_id FROM posts 
    WHERE last_comment_fetch IS NULL
    ORDER BY created_utc DESC
''')
all_posts = cursor.fetchall()

# Total number of posts to process
total_posts = len(all_posts)
print(f"\nFetching Comments for {total_posts} Posts...\n")

total_comments_added = 0
post_count = 0
skipped_posts = 0
start_time = time.time()

# Loop through each post
for i, (post_id,) in enumerate(all_posts, start=1):
    try:
        # Log start time of processing each post
        start_time_post = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{start_time_post}] Starting to fetch comments for post {post_id} ({i}/{total_posts})")

        post = reddit.submission(id=post_id)
        post.comment_sort = 'new'
        post.comments.replace_more(limit=None)

        post_comments = []
        for comment in post.comments.list():
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

        # Commit comments and update post info after each post is processed
        conn.commit()
        post_count += 1

        # Update the num_comments and last_comment_fetch fields for the post
        cursor.execute('''
            UPDATE posts 
            SET num_comments = ?, last_comment_fetch = ? 
            WHERE post_id = ?
        ''', (
            len(post_comments),   # Number of comments fetched
            time.time(),          # Current timestamp
            post_id               # Post identifier
        ))
        conn.commit()

        # Reduced delay to 0.1 seconds to speed up the process
        time.sleep(0.5)

        # Log end time of processing each post
        end_time_post = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{end_time_post}] Finished fetching for post {post_id}. Comments added: {len(post_comments)}")

        # Update progress
        percent_complete = (i / total_posts) * 100
        sys.stdout.write(f"\rProgress: {i} / {total_posts} posts processed ({percent_complete:.1f}% completed)")
        sys.stdout.flush()

    except Exception as e:
        print(f"\nError processing post {post_id}: {e}")
        skipped_posts += 1
        continue  # Move on to the next post

end_time = time.time()
time_taken = round((end_time - start_time) / 60, 2)  # Time in minutes

# Close the database connection
conn.close()

# Final summary
print("\n\nFinal Summary:")
print(f"- Total posts processed: {post_count}")
print(f"- Total comments added: {total_comments_added}")
print(f"- Skipped posts due to errors: {skipped_posts}")
print(f"- Time taken: {time_taken} minutes")