from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'
client = MongoClient('mongodb://localhost:27017/')
db = client.hrms
users = db.users
employees = db.employees
reviews = db.reviews

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, username, is_hr=False):
        self.username = username
        self.is_hr = is_hr

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(username):
    user = users.find_one({"username": username})
    if user:
        return User(username=user['username'], is_hr=user['is_hr'])
    return None

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({"username": username})

        if user and check_password_hash(user['password'], password):
            login_user(User(username=user['username'], is_hr=user['is_hr']))
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_hr = 'is_hr' in request.form

        if users.find_one({"username": username}):
            flash('Username already exists.')
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            users.insert_one({
                "username": username,
                "password": hashed_password,
                "is_hr": is_hr
            })
            flash('Account created successfully! Please log in.')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/employees')
@login_required
def employee_list():
    employees_list = employees.find()
    return render_template('employee_list.html', employees=employees_list)

@app.route('/employee/new', methods=['GET', 'POST'])
@login_required
def new_employee():
    if not current_user.is_hr:
        flash('Access denied.')
        return redirect(url_for('employee_list'))

    if request.method == 'POST':
        employees.insert_one({
            "name": request.form['name'],
            "position": request.form['position'],
            "department": request.form['department'],
            "hire_date": request.form['hire_date']
        })
        return redirect(url_for('employee_list'))
    return render_template('employee_form.html', form_action='New')

@app.route('/employee/<employee_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_employee(employee_id):
    if not current_user.is_hr:
        flash('Access denied.')
        return redirect(url_for('employee_list'))

    employee = employees.find_one({"_id": ObjectId(employee_id)})

    if request.method == 'POST':
        employees.update_one(
            {"_id": ObjectId(employee_id)},
            {"$set": {
                "name": request.form['name'],
                "position": request.form['position'],
                "department": request.form['department'],
                "hire_date": request.form['hire_date']
            }}
        )
        return redirect(url_for('employee_list'))
    
    return render_template('employee_form.html', form_action='Edit', employee=employee)

@app.route('/employee/<employee_id>/delete', methods=['POST'])
@login_required
def delete_employee(employee_id):
    if not current_user.is_hr:
        flash('Access denied.')
        return redirect(url_for('employee_list'))

    employees.delete_one({"_id": ObjectId(employee_id)})
    return redirect(url_for('employee_list'))

@app.route('/reviews')
@login_required
def review_list():
    reviews_list = reviews.find()
    return render_template('review_list.html', reviews=reviews_list)

@app.route('/review/new', methods=['GET', 'POST'])
@login_required
def new_review():
    if not current_user.is_hr:
        flash('Access denied.')
        return redirect(url_for('review_list'))

    if request.method == 'POST':
        reviews.insert_one({
            "employee_id": ObjectId(request.form['employee_id']),
            "reviewer": current_user.username,
            "date": request.form['date'],
            "rating": request.form['rating'],
            "comments": request.form['comments']
        })
        return redirect(url_for('review_list'))
    
    employees_list = employees.find()
    return render_template('review_form.html', form_action='New', employees=employees_list)

@app.route('/review/<review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    if not current_user.is_hr:
        flash('Access denied.')
        return redirect(url_for('review_list'))

    review = reviews.find_one({"_id": ObjectId(review_id)})

    if request.method == 'POST':
        reviews.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": {
                "employee_id": ObjectId(request.form['employee_id']),
                "reviewer": current_user.username,
                "date": request.form['date'],
                "rating": request.form['rating'],
                "comments": request.form['comments']
            }}
        )
        return redirect(url_for('review_list'))
    
    employees_list = employees.find()
    return render_template('review_form.html', form_action='Edit', review=review, employees=employees_list)

@app.route('/review/<review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    if not current_user.is_hr:
        flash('Access denied.')
        return redirect(url_for('review_list'))

    reviews.delete_one({"_id": ObjectId(review_id)})
    return redirect(url_for('review_list'))

@app.route('/review/<review_id>')
@login_required
def view_review(review_id):
    review = reviews.find_one({"_id": ObjectId(review_id)})
    return render_template('review_detail.html', review=review)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
