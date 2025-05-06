import streamlit as st
import os
import json
import bcrypt
from datetime import datetime, timedelta

class Authentication:
    def __init__(self):
        self.users_db_path = "data/users.json"
        os.makedirs("data", exist_ok=True)
        self.load_users()
    
    def load_users(self):
        """Load users from database file."""
        if os.path.exists(self.users_db_path):
            with open(self.users_db_path, 'r') as f:
                self.users = json.load(f)
        else:
            # Initialize with empty users dict
            self.users = {}
            self.save_users()
    
    def save_users(self):
        """Save users to database file."""
        with open(self.users_db_path, 'w') as f:
            json.dump(self.users, f)
    
    def register_user(self, username, password, email):
        """Register a new user."""
        if username in self.users:
            return False, "Username already exists"
        
        # Hash the password
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user entry
        self.users[username] = {
            'password_hash': hashed_pw.decode('utf-8'),
            'email': email,
            'joined_date': datetime.now().strftime('%Y-%m-%d'),
            'last_login': None,
            'profile': {
                'bio': '',
                'avatar': ''
            }
        }
        
        self.save_users()
        return True, "Registration successful"
    
    def authenticate(self, username, password):
        """Authenticate a user."""
        if username not in self.users:
            return False, "Invalid username or password"
        
        stored_hash = self.users[username]['password_hash'].encode('utf-8')
        
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            # Update last login time
            self.users[username]['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.save_users()
            return True, "Authentication successful"
        
        return False, "Invalid username or password"
    
    def get_user_profile(self, username):
        """Get user profile information."""
        if username in self.users:
            return self.users[username]
        return None
    
    def update_user_profile(self, username, profile_data):
        """Update user profile information."""
        if username in self.users:
            self.users[username]['profile'].update(profile_data)
            self.save_users()
            return True
        return False
