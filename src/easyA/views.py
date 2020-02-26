from easyA import app
from easyA import db

from flask import render_template, request, session, redirect, url_for
import google.cloud
import requests
import json
import datetime

firestore_database, realtime_database, firebase_wrapper = db.init_db()
auth = firebase_wrapper.auth()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/verified_user')
def display():
    return render_template('verified_user.html')    

@app.route('/signout')
def signout():
    session.pop('email', None)
    session.pop('password', None)
    return redirect(url_for('index'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        return do_login()
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':      
        return do_signup()
    return render_template('signup.html')


@app.route( '/course/')
@app.route('/course/<course_id>')
def course_page(course_id, get_info=False):
    posts = []
    courses_ref = firestore_database.collection('courses').where('course_id', '==', course_id)
    
    for course in courses_ref.stream():
        course_dic = course.to_dict()
        course_id = course_dic['course_id']
        course_name = course_dic['course_name']
        description = course_dic['description']
        rating = course_dic['rating']
        rating_count = course_dic['rating_count']
        post_ref = firestore_database.collection('posts').where('course', '==', course.reference).stream()
        for post in post_ref:
            posts.append(post.to_dict())

    if get_info:
        return course, course_id, course_name
    return render_template('class.html', course_id=course_id, course_name=course_name, description=description, rating=rating, rating_count=rating_count, posts=posts)

@app.route('/course/<course_id>/new_review', methods=['POST', 'GET'])
def new_review(course_id):
    if session['email'] is None:
        return redirect('/course/' + course_id)
    professors = []
    course, course_id, course_name = course_page(course_id, True)
    if request.method == 'POST':
        return post_review(course, course_id)
    
    professor_ref = firestore_database.collection('professors').where('course', '==', course.reference).stream()
    for professor in professor_ref:
        professors.append(professor.to_dict())
    return render_template('new_review.html', course_id=course_id, course_name=course_name, professors=professors)

#Posting function
def post_review(course, course_id):
    career_id = (session['email'].split('@', 2))[0]
    author = firestore_database.collection('users').document(career_id).get()
    data = {
        "posted_date": datetime.datetime.now().isoformat(),
        "author": author.reference,
        "course": course.reference,
        "professor": request.form['professor'],
        "attendance": request.form['attendance'],
        "textbook": request.form['textbook'],
        "grade": request.form['grade'],
        "rating": int(request.form['rating']),
        "tags": "",
        "text": request.form['text'],
        "report_count": 0,
        "downvotes": 0,
        "upvotes": 0
    }

    #Increment post count for the course
    post_count = course.to_dict()['rating_count'] + 1
    course.reference.update({
        "rating_count": post_count
    })

    #Add the post to the database
    firestore_database.collection('posts').add(data)

    return redirect('/course/' + str(course_id))

#Login function
def do_login():
    email = request.form['u_email']
    password = request.form['u_password']


    try:
        session['email'] = email
        session['password'] = password
        print(session['email'])
        print(session['password'])
        auth.sign_in_with_email_and_password(session['email'], session['password'])
        print("User logged in successfully")
        return redirect(url_for('index'))
    except requests.exceptions.HTTPError as e:
        #Create a dictionary from the error
        e_dict = json.loads(e.strerror)

        #Check if a credentials error occured
        if e_dict["error"]["message"] == "INVALID_PASSWORD" or e_dict["error"]["message"] == "EMAIL_NOT_FOUND":
            print("Incorrect credentials!")
            return login()
        else:
            #Print error code and message
            print("HTTPError Code {}: {}".format(e_dict["error"]["code"], e_dict["error"]["message"]))
            return login()

#Sign up function
def do_signup():
    email = request.form['u_email']
    password = request.form['u_password']
    confirm_password = request.form['u_confirm_password']

    #Check user input for password confirmation
    if password != confirm_password:
        print("Unmatching password")
        return signup()

    email_parts = email.split('@', 2)

    #Check user input for "@purdue.edu"
    if email_parts[1].casefold() != "purdue.edu":
        print("Unsupported email")
        return signup()

    #Check if user's career ID exists in the database
    career_id = email_parts[0]
    user_ref = firestore_database.collection('users').document(career_id)

    if user_ref.get().exists:
        print("User {} already exists!".format(user_ref.get().to_dict()))
        return signup()
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

            print('Signup Successful')
            
            #Log in
            return do_login()
        except requests.exceptions.HTTPError as e:
            #Create a dictionary from the error
            e_dict = json.loads(e.strerror)

            #Print error code and message
            print("HTTPError Code {}: {}".format(e_dict["error"]["code"], e_dict["error"]["message"]))
            return signup()
        except Exception as e:
            print("Authentication or Database FAILURE - {}".format(e))
            return signup()

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')