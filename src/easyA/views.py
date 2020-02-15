from flask import Blueprint, render_template


#Blueprint for the flask app
views_app = Blueprint('views_app', __name__, template_folder = 'templates')

@views_app.route('/')
def index():
    return render_template('home.html')

@views_app.route('/login')
def login():
    return render_template('login.html')

@views_app.route('/signup')
def signup():
    return render_template('signup.html')
