from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client.hrms

# Collections
employees = db.employees
performance_reviews = db.performance_reviews
users = db.users

# Ensure indexes for unique fields
users.create_index("username", unique=True)

def create_user(username, password, is_hr):
    hash_password = generate_password_hash(password)
    users.insert_one({"username": username, "password": hash_password, "is_hr": is_hr})

def check_user(username, password):
    user = users.find_one({"username": username})
    if user and check_password_hash(user['password'], password):
        return user
    return None

def find_user(username):
    return users.find_one({"username": username})
