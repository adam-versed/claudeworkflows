#!/usr/bin/env python3
"""
Test application with intentional security issues for demonstration.
"""

import sqlite3
import requests

# Security Issue: Hardcoded credentials
DATABASE_PASSWORD = "super_secret_123"
API_KEY = "sk-abcd1234567890abcdef1234567890"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

class UserAuth:
    def __init__(self):
        # Security Issue: Hardcoded database connection
        self.db_url = "postgresql://admin:password123@localhost:5432/myapp"
        
    def authenticate(self, username, password):
        # Security Issue: SQL injection vulnerability
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def get_user_data(self, user_input):
        # Security Issue: No input validation
        return eval(user_input)  # Never do this!

def make_api_call(endpoint):
    # Security Issue: API key in code
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": "MyApp/1.0"
    }
    
    # Security Issue: No SSL verification
    response = requests.get(endpoint, headers=headers, verify=False)
    return response.json()

# Security Issue: Hardcoded JWT secret
JWT_SECRET = "my-very-secret-jwt-key-that-should-not-be-here"

if __name__ == "__main__":
    auth = UserAuth()
    
    # Test with user input (dangerous!)
    user_data = auth.get_user_data("__import__('os').system('ls')")
    print("User data:", user_data)