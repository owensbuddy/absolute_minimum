import sys
import os
import praw
import json
import sqlite3

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

# Define function to insert a post into the database
def insert_post(post_data):
    cursor.execute('''
        INSERT OR IGNORE INTO posts (post_id, subreddit, title, score, author, created_utc, num_comments, selftext, url, permalink)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        post_data['id'],
        post_data['subreddit'],
        post_data['title'],
        post_data['score'],
        post_data['author'],
        post_data['created_utc'],
        post_data['num_comments'],
        post_data['selftext'],
        post_data['url'],
        post_data['permalink']
    ))

# List of subreddits to fetch
subreddits_to_fetch = ["WGUMSCSIA", "WGUAccelerators", "WGU_Business", "WGUTeachersAlumni", "WGU_MSDA", "WGU_CSA", 
                       "WGU_Accelerators", "WGU_MSMK", "WGU_Military", "WGU_BSHIM", "WGU_CompSci", "wguaccounting", 
                       "WGUFINALEXAMs_OAs_PAs", "WGU_MAEdTech0724", "WGUIT", "WGU_Study_Guide", "WGUBusinessManagement", 
                       "WGU", "WGU_RNtoBSN", "WGU_CloudComputing", "wguitsec", "WGU_BSIT", "WGUAcademy", "WGUMSHRM", 
                       "wgu_devs", "WGU_DataAnalytics", "WGU_Cloud_Computing", "WGU_MSLxD", "WGU_SWE", "WGU_HumanResources", 
                       "WGUHelpReddit_", "WGUTeachersCollege", "WGUPSYCHOLOGY2425", "WGU_HHS", "WGUfinance", "wgu_msitm", 
                       "WGUCyberSecurityClub", "WGUonline", "wgu_ITnetworking", "WguTutorReddit", "WGU_MSDA_June2023", 
                       "WGU_BSSE", "WGU_Psychology", "WGUCyberSecurity", "WGU_Finance", "WGUhumanresources", "WGU_BSSCOM", 
                       "WGU_MBA", "u_wgu-social-media", "WGU_NURSING", "wgueducation", "WGU_ClassesHelp", "WGU_MktgMgmt", 
                       "wgu_employees"]

total_posts_added = 0
all_recent_posts = []

for index, subreddit_name in enumerate(subreddits_to_fetch, start=1):
    # Get the most recent post timestamp in the database
    cursor.execute('SELECT MAX(created_utc) FROM posts WHERE subreddit = ?', (subreddit_name,))
    max_created_utc = cursor.fetchone()[0]

    # Fetch new posts from Reddit
    subreddit = reddit.subreddit(subreddit_name)
    new_posts = []
    subreddit_post_count = 0

    for post in subreddit.new(limit=1000):  # Adjust limit as needed
        # Only add posts newer than the latest in the database
        if max_created_utc and post.created_utc <= max_created_utc:
            break

        # Post data to store
        post_data = {
            'id': post.id,
            'subreddit': post.subreddit.display_name,
            'title': post.title,
            'score': post.score,
            'author': post.author.name if post.author else None,
            'created_utc': post.created_utc,
            'num_comments': post.num_comments,
            'selftext': post.selftext,
            'url': post.url,
            'permalink': post.permalink
        }

        # Insert new post into database and count it
        insert_post(post_data)
        subreddit_post_count += 1
        new_posts.append(post_data)

    # Commit changes for this subreddit and show progress in a single line
    conn.commit()
    total_posts_added += subreddit_post_count
    print(f"{subreddit_name}: {subreddit_post_count} new posts added.")

    # Accumulate all new posts for optional JSON saving
    all_recent_posts.extend(new_posts)

# Summary of added posts
print(f"\nSummary: {total_posts_added} new posts added across {len(subreddits_to_fetch)} subreddits.")

# Save posts to JSON file if needed
output_path = '/Users/buddy/Desktop/School/effective-adventure/effective-adventure/data/recent_posts.json'
print(f"\nSaving recent posts to JSON file at {output_path}...")
with open(output_path, 'w') as f:
    json.dump(all_recent_posts, f, indent=4)
print("Recent posts saved to JSON file successfully.")

# Close the database connection
conn.close()
print("Database connection closed.")