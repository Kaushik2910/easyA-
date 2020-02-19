
from easyA import app
from flask import render_template


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/class')
def class():
    return render_template('class.html')

@app.route('/new_review')
def new_review():
    return render_template('login.html')

@app.route('/contact')
def contact():
    return render_template('signup.html')

@app.route('/report')
def report():
    return render_template('class.html')
