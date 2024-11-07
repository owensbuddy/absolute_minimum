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

# Helper function to insert a comment into the database
def insert_comment(comment_data):
    cursor.execute('''
        INSERT OR IGNORE INTO comments_new (comment_id, post_id, parent_id, author, content, upvotes, created_utc, ratio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        comment_data['comment_id'],
        comment_data['post_id'],
        comment_data['parent_id'],
        comment_data['author'],
        comment_data['content'],
        comment_data['upvotes'],
        comment_data['created_utc'],
        comment_data['ratio']
    ))

# Helper function to save data to JSON
def save_to_json(data, path):
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)

# Get the most recent post's created_utc from the posts table
cursor.execute('SELECT MAX(created_utc) FROM posts')
result = cursor.fetchone()
last_post_time = result[0] if result and result[0] else 0
print(f"Most recent post in database was created at {datetime.utcfromtimestamp(last_post_time)} UTC")

# Fetch list of subreddits
cursor.execute('SELECT subreddit FROM subreddits')
subreddits = cursor.fetchall()
subreddit_list = [sub[0] for sub in subreddits]
print(f"Fetching new posts from the following subreddits: {', '.join(subreddit_list)}")

# Initialize data storage for JSON
posts_data = []
total_posts_added = 0
total_comments_added = 0

# Loop through each subreddit
for subreddit_name in subreddit_list:
    print(f"\nFetching new posts from r/{subreddit_name}")
    subreddit = reddit.subreddit(subreddit_name)
    try:
        new_posts = subreddit.new(limit=1000)
        for post in new_posts:
            if post.created_utc > last_post_time:
                print(f"Processing post {post.id} created at {datetime.utcfromtimestamp(post.created_utc)} UTC")

                # Collect post data
                post_data = {
                    'post_id': post.id,
                    'subreddit': subreddit_name,
                    'title': post.title,
                    'score': post.score,
                    'author': post.author.name if post.author else None,
                    'created_utc': post.created_utc,
                    'num_comments': post.num_comments,
                    'selftext': post.selftext,
                    'url': post.url,
                    'permalink': post.permalink
                }
                
                # Insert post into the database
                cursor.execute('''
                    INSERT OR IGNORE INTO posts (
                        post_id, subreddit, title, score, author, created_utc, 
                        num_comments, selftext, url, permalink, comments_fetched, last_comment_fetch
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_data['post_id'],
                    post_data['subreddit'],
                    post_data['title'],
                    post_data['score'],
                    post_data['author'],
                    post_data['created_utc'],
                    post_data['num_comments'],
                    post_data['selftext'],
                    post_data['url'],
                    post_data['permalink'],
                    0,      # comments_fetched
                    None    # last_comment_fetch
                ))
                conn.commit()
                total_posts_added += 1

                # Fetch comments for the post
                print(f"Fetching comments for post {post.id}")
                post.comment_sort = 'new'
                post.comments.replace_more(limit=None)
                comments_data = []
                for comment in post.comments.list():
                    comment_data = {
                        'comment_id': comment.id,
                        'post_id': post.id,
                        'parent_id': comment.parent_id,
                        'author': comment.author.name if comment.author else None,
                        'content': comment.body,
                        'upvotes': comment.score,
                        'created_utc': comment.created_utc,
                        'ratio': None  # No ratio calculation
                    }
                    insert_comment(comment_data)
                    total_comments_added += 1
                    comments_data.append(comment_data)
                conn.commit()

                # Update comments_fetched and last_comment_fetch in posts table
                cursor.execute('''
                    UPDATE posts SET comments_fetched = ?, last_comment_fetch = ?
                    WHERE post_id = ?
                ''', (
                    1,      # comments_fetched
                    time.time(),  # last_comment_fetch
                    post.id
                ))
                conn.commit()

                # Add comments to post_data
                post_data['comments'] = comments_data

                # Add post_data to posts_data list
                posts_data.append(post_data)

                # Respect API rate limits
                time.sleep(0.5)

            else:
                print(f"Reached posts older than the most recent post in database. Moving to next subreddit.")
                break

    except Exception as e:
        print(f"Error fetching posts from r/{subreddit_name}: {e}")
        continue

# Save posts_data to JSON
save_to_json(posts_data, '/Users/buddy/Desktop/School/effective-adventure/effective-adventure/data/recent_posts_comments.json')

# Close the database connection
conn.close()

# Final summary
print("\nFinal Summary:")
print(f"- Total new posts added: {total_posts_added}")
print(f"- Total new comments added: {total_comments_added}")
print(f"- Data saved to recent_posts_comments.json")