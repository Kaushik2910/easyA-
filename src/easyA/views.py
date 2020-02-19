
from easyA import app
from easyA import db

from flask import render_template, request
import google.cloud
import requests
import json

firestore_database, realtime_database, firebase_wrapper = db.init_db()
auth = firebase_wrapper.auth()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/course')
def course():
    return render_template('course.html')

@app.route('/new_review')
def new_review():
    return render_template('new_review.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        do_login()
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        do_signup()
    return render_template('signup.html')

#Login function
def do_login():
    email = request.form['u_email']
    password = request.form['u_password']

    try:
        auth.sign_in_with_email_and_password(email, password)
        print("User logged in successfully")
        return
    except requests.exceptions.HTTPError as e:
        #Create a dictionary from the error
        e_dict = json.loads(e.strerror)

        #Check if a credentials error occured
        if e_dict["error"]["message"] == "INVALID_PASSWORD" or e_dict["error"]["message"] == "EMAIL_NOT_FOUND":
            print("Incorrect credentials!")
            return
        else:
            #Print error code and message
            print("HTTPError Code {}: {}".format(e_dict["error"]["code"], e_dict["error"]["message"]))
            return

#Sign up function
def do_signup():
    email = request.form['u_email']
    password = request.form['u_password']

    email_parts = email.split('@', 2)

    #Check user input for "@purdue.edu"
    if email_parts[1].casefold() != "@purdue.edu":
        print("Unsupported email")
        return

    #Check if user's career ID exists in the database
    career_id = email_parts[0]
    user_ref = firestore_database.collection('users').document(career_id)

    if user_ref.get().exists:
        print("User {} already exists!".format(user_ref.get().to_dict()))
        return
    else:
        try:
            #Create user
            auth.create_user_with_email_and_password(email, password)

            #Record the user in the database
            data = {
                "email": email,
            }
            firestore_database.collection('users').document(career_id).set(data)

            #Log in
            do_login()

            print('Signup and Login Successful')
            return
        except requests.exceptions.HTTPError as e:
            #Create a dictionary from the error
            e_dict = json.loads(e.strerror)

            #Print error code and message
            print("HTTPError Code {}: {}".format(e_dict["error"]["code"], e_dict["error"]["message"]))
            return
        except Exception as e:
            print("Authentication or Database FAILURE - {}".format(e))
            return
