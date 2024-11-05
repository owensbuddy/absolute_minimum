WGU Reddit Social Media Management Tool

Project Overview

This tool gathers and analyzes Reddit discussions across 52 WGU-related subreddits, storing data on posts, comments, users, and subreddits for insights into community engagement.

Key Goals

	1.	Database Setup: Store relevant data across four main tables:
	•	Subreddits: Details per WGU subreddit.
	•	Users: User data, including moderation roles.
	•	Posts: Basic post information.
	•	Comments: Nested structure for replies.
	2.	Core Scripts:
	•	initialize_database.py: Set up database tables and schema.
	•	update_database.py: Daily data updates.
	•	fetch_subreddit_info.py: Gather subreddit attributes.
	•	fetch_user_info.py: Collect user details.
	•	show_files_db.py: Display database structure and file tree.
	3.	Data Categorization: Initial manual topic categorization for posts; future expansion to machine learning-based categorization.
	4.	Dashboard Development: Create views for each table with key metrics.

Development Status

	•	Database Setup: Done
	•	Comment Hierarchy Fix: Done (new comments_new table)
	•	Data Collection Scripts:
	•	fetch_subreddit_info.py: To Do
	•	fetch_user_info.py: To Do
	•	Daily Update: Done
	•	Database Inspection: Done
	•	ETL Process: In Progress
	•	Dashboard Views: To Do
	•	Post Categorization: Manual (In Progress), ML (Future Work)