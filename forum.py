import streamlit as st
import os
import json
from datetime import datetime
import uuid

class ForumManager:
    def __init__(self):
        self.posts_db_path = "data/forum_posts.json"
        self.comments_db_path = "data/forum_comments.json"
        os.makedirs("data", exist_ok=True)
        self.load_data()
    
    def load_data(self):
        """Load forum data from database files."""
        if os.path.exists(self.posts_db_path):
            with open(self.posts_db_path, 'r') as f:
                self.posts = json.load(f)
        else:
            self.posts = []
            self.save_posts()
            
        if os.path.exists(self.comments_db_path):
            with open(self.comments_db_path, 'r') as f:
                self.comments = json.load(f)
        else:
            self.comments = {}
            self.save_comments()
    
    def save_posts(self):
        """Save posts to database file."""
        with open(self.posts_db_path, 'w') as f:
            json.dump(self.posts, f)
    
    def save_comments(self):
        """Save comments to database file."""
        with open(self.comments_db_path, 'w') as f:
            json.dump(self.comments, f)
    
    def create_post(self, username, title, content, category):
        """Create a new forum post."""
        post_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        new_post = {
            'id': post_id,
            'author': username,
            'title': title,
            'content': content,
            'category': category,
            'timestamp': timestamp,
            'likes': 0,
            'liked_by': []
        }
        
        self.posts.append(new_post)
        self.comments[post_id] = []
        
        self.save_posts()
        self.save_comments()
        
        return post_id
    
    def get_posts(self, category=None):
        """Get all posts, optionally filtered by category."""
        if category:
            return [post for post in self.posts if post['category'] == category]
        return self.posts
    
    def get_post(self, post_id):
        """Get a specific post by ID."""
        for post in self.posts:
            if post['id'] == post_id:
                return post
        return None
    
    def add_comment(self, post_id, username, content):
        """Add a comment to a post."""
        if post_id not in self.comments:
            self.comments[post_id] = []
            
        comment = {
            'id': str(uuid.uuid4()),
            'author': username,
            'content': content,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'likes': 0
        }
        
        self.comments[post_id].append(comment)
        self.save_comments()
        
        return True
    
    def get_comments(self, post_id):
        """Get all comments for a post."""
        return self.comments.get(post_id, [])
    
    def like_post(self, post_id, username):
        """Like or unlike a post."""
        for post in self.posts:
            if post['id'] == post_id:
                if username in post['liked_by']:
                    post['liked_by'].remove(username)
                    post['likes'] -= 1
                else:
                    post['liked_by'].append(username)
                    post['likes'] += 1
                self.save_posts()
                return True
        return False
