import sys
import os
import praw
import json
import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from pathlib import Path
import time

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

# Configuration constants
DAYS_TO_FETCH = 1  # Fetch posts from the last day
BATCH_SIZE = 100   # Number of comments to process before committing
RATE_LIMIT_PAUSE = 1  # Seconds to wait between API calls

def calculate_ratio(comment_score: int, parent_score: int) -> float:
    if parent_score == 0:
        return 1.0 if comment_score == 0 else float(comment_score)
    comment_sign = 1 if comment_score >= 0 else -1
    parent_sign = 1 if parent_score >= 0 else -1
    ratio = abs(comment_score) / abs(parent_score)
    return ratio * (comment_sign * parent_sign)

class RedditScraper:
    def __init__(self, reddit_instance, db_path: str):
        self._setup_logging()
        self.reddit = reddit_instance
        self.db_path = db_path
        self.conn = self._init_database()
        self.cursor = self.conn.cursor()
        self.cutoff_time = datetime.now(timezone.utc) - timedelta(days=DAYS_TO_FETCH)
        logging.info(f"Fetching comments from posts made in the last {DAYS_TO_FETCH} day(s)")

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('reddit_scraper.log'),
                logging.StreamHandler()
            ]
        )

    def _init_database(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.db_path)
            # Ensures the comments_new table exists
            conn.execute('''
                CREATE TABLE IF NOT EXISTS comments_new (
                    id INTEGER PRIMARY KEY,
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
            conn.execute('PRAGMA journal_mode=WAL')
            return conn
        except Exception as e:
            logging.error(f"Failed to connect to database: {str(e)}")
            raise

    def insert_comments_batch(self, comments: List[Dict]):
        try:
            self.cursor.executemany('''
                INSERT OR IGNORE INTO comments_new 
                (comment_id, post_id, parent_id, author, content, upvotes, created_utc, ratio)
                VALUES (:id, :post_id, :parent_id, :author, :content, :upvotes, :created_utc, :ratio)
            ''', comments)
            self.conn.commit()
            time.sleep(RATE_LIMIT_PAUSE)
        except Exception as e:
            logging.error(f"Failed to insert comments batch into comments_new: {str(e)}")
            self.conn.rollback()
            raise

    def process_post_comments(self, post_id: str) -> int:
        try:
            post = self.reddit.submission(id=post_id)
            post.comment_sort = 'new'
            post.comments.replace_more(limit=None)
            comments_batch = []
            comments_processed = 0
            comment_scores = {f"t3_{post.id}": post.score}
            
            for comment in post.comments.list():
                comment_scores[f"t1_{comment.id}"] = comment.score
            
            for comment in post.comments.list():
                if comment.created_utc >= self.cutoff_time.timestamp():
                    parent_id = comment.parent_id
                    parent_score = comment_scores.get(parent_id, 0)
                    comment_data = {
                        'id': comment.id,
                        'post_id': post_id,
                        'parent_id': parent_id[3:],
                        'author': comment.author.name if comment.author else None,
                        'content': comment.body,
                        'upvotes': comment.score,
                        'created_utc': comment.created_utc,
                        'ratio': calculate_ratio(comment.score, parent_score)
                    }
                    comments_batch.append(comment_data)
                    comments_processed += 1
                    
                    if len(comments_batch) >= BATCH_SIZE:
                        self.insert_comments_batch(comments_batch)
                        comments_batch = []
                        
            if comments_batch:
                self.insert_comments_batch(comments_batch)
                
            return comments_processed
        except Exception as e:
            logging.error(f"Error processing post {post_id}: {str(e)}")
            return 0

    def fetch_and_process_posts(self):
        total_processed = 0
        try:
            # Fetch posts from the last 1 day where comments haven't been fetched recently
            self.cursor.execute("""
                SELECT post_id FROM posts 
                WHERE created_utc >= ? 
                AND (comments_fetched = 0 OR last_comment_fetch < ?)
            """, (self.cutoff_time.timestamp(), self.cutoff_time.timestamp()))
            
            post_ids = [row[0] for row in self.cursor.fetchall()]
            
            for post_id in post_ids:
                processed = self.process_post_comments(post_id)
                total_processed += processed
                # Update comments_fetched and last_comment_fetch in the posts table
                self.cursor.execute("""
                    UPDATE posts SET comments_fetched = 1, last_comment_fetch = ? 
                    WHERE post_id = ?
                """, (datetime.now(timezone.utc).timestamp(), post_id))
                self.conn.commit()
                logging.info(f"Processed {processed} comments from post {post_id}")
                time.sleep(RATE_LIMIT_PAUSE)
            
            logging.info(f"Total comments processed: {total_processed}")
        except Exception as e:
            logging.error(f"Error fetching posts: {str(e)}")

    def run(self):
        try:
            self.fetch_and_process_posts()
        except Exception as e:
            logging.error(f"Fatal error during execution: {str(e)}")
            raise
        finally:
            if self.conn:
                self.conn.close()

def main():
    db_path = '/Users/buddy/Desktop/School/effective-adventure/effective-adventure/db/WGU_Reddit.db'
    
    try:
        scraper = RedditScraper(reddit, db_path)
        scraper.run()
    except Exception as e:
        logging.error(f"Application failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()