from easyA import app
from easyA import db

from flask import render_template, request, session
import google.cloud
import requests
import json

firestore_database, realtime_database, firebase_wrapper = db.init_db()
auth = firebase_wrapper.auth()
Email="False"
@app.route('/')
def index():
    return render_template('home.html', email=Email)

@app.route('/verified_user')
def display():
    return render_template('verified_user.html')    


@app.route('/signout')
def signout():

    session.pop('username', None)
    session.pop('password', None)
    return render_template('home.html')

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

@app.route('/course/')
@app.route('/course/<course_id>')
def course_page(course_id):
    posts = []
    course_ref = firestore_database.collection('courses').where('course_id', '==', course_id)
    
    for course in course_ref.stream():
        course_dic = course.to_dict()
        course_id = course_dic['course_id']
        course_name = course_dic['course_name']
        rating = course_dic['rating']
        rating_count = course_dic['rating_count']
        post_ref = firestore_database.collection('posts').where('course', '==', course.reference).stream()
        for post in post_ref:
            posts.append(post.to_dict())

    return render_template('class.html', course_id=course_id, course_name=course_name, rating=rating, rating_count=rating_count, posts=posts)

#Login function
def do_login():
    global Email
    email = request.form['u_email']
    password = request.form['u_password']


    try:
        session['email'] = email
        session['password'] = password
        print(session['email'])
        print(session['password'])
        auth.sign_in_with_email_and_password(session['email'], session['password'])
        print("User logged in successfully")
        Email=email
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
    if email_parts[1].casefold() != "purdue.edu":
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
            session['email']=email
            session['password']=password

            user = auth.create_user_with_email_and_password(session['email'], session['password'])

            #Send email verification
            auth.send_email_verification(user['idToken'])

            #Record the user in the database
            data = {
                "email": session['email'],
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

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')