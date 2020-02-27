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

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/reset_pwd')
def reset_pwd():
    return render_template('reset_pwd.html')

@app.route('/forgot_pwd')
def forgot_pwd():
    return render_template('forgot_pwd.html')

@app.route('/signout')
def signout():
    session.pop('email', None)
    session.pop('password', None)
    return redirect(url_for('index'))

@app.route('/login', methods=['POST', 'GET'])
def login(errorMessage="", requestTrigger=True):
    if (request.method == 'POST') and requestTrigger:
        return do_login()
    return render_template('login.html', errorMessage=errorMessage)

@app.route('/signup', methods=['POST', 'GET'])
def signup(errorMessage="", requestTrigger=True):
    if (request.method == 'POST') and requestTrigger:
        return do_signup()
    return render_template('signup.html', errorMessage=errorMessage)


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
        rating = 0
        rating_count = 0
        post_ref = firestore_database.collection('posts').where('course', '==', course.reference).stream()
        for post in post_ref:
            tempDict = post.to_dict()
            tempDict['post_ID'] = post.id

            #Sum all course rating
            rating += tempDict['rating']
            rating_count += 1

            posts.append(tempDict)

        #Calculate average rating
        if rating_count != 0:
            rating = int(rating / rating_count)
        else:
            rating = 0

    if get_info:
        return course, course_id, course_name
    return render_template('course.html', course_id=course_id, course_name=course_name, description=description, rating=rating, rating_count=rating_count, posts=posts)

@app.route('/course/<course_id>/new_review', methods=['POST', 'GET'])
def new_review(course_id):
    if 'email' not in session:
        return redirect('/course/' + course_id)
    professors = []
    course, course_id, course_name = course_page(course_id, True)
    if request.method == 'POST':
        return post_review(course, course_id)

    professor_ref = firestore_database.collection('professors').where('course', '==', course.reference).stream()
    for professor in professor_ref:
        professors.append(professor.to_dict())
    return render_template('new_review.html', course_id=course_id, course_name=course_name, professors=professors)

@app.route('/report', methods=['POST', 'GET'])
def report():
    if request.method == 'POST':
        print(request.form['post_ID'])
        return render_template('report.html', post=request.form['post_ID'])

    return redirect(url_for('index'))

#Posting a report function
@app.route('/post_report', methods=['POST', 'GET'])
def post_report():
    if request.method == 'POST':
        career_id = (session['email'].split('@', 2))[0]
        author = firestore_database.collection('users').document(career_id).get()
        post = request.form['post_object']
        print(post)
        data = {
            "report_date": datetime.datetime.now().isoformat(),
            "author": author.reference,
            "report_post": post.reference,
            "text": request.form['text'],
        }

        #Increment post count for the course
        report_count = post.to_dict()['report_count'] + 1
        post.reference.update({
            "report_count": int(report_count)
        })

        #Add the report to the database
        firestore_database.collection('reports').add(data)

        return redirect('/course/' + str(post.to_dict()['course'].to_dict()['course_id']))

    return redirect(url_for('index'))

#Posting a review function
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

    #Add the post to the database
    firestore_database.collection('posts').add(data)

    return redirect('/course/' + str(course_id))

#Login function
def do_login():
    email = request.form['u_email']
    password = request.form['u_password']

    try:
        auth.sign_in_with_email_and_password(email, password)
        session['email'] = email
        session['password'] = password
        print("User logged in successfully")
        return redirect(url_for('index'))
    except requests.exceptions.HTTPError as e:
        #Create a dictionary from the error
        e_dict = json.loads(e.strerror)

        #Check if a credentials error occured
        if e_dict["error"]["message"] == "INVALID_PASSWORD" or e_dict["error"]["message"] == "EMAIL_NOT_FOUND":
            return login("Incorrect credentials!", False)
        else:
            #Print error code and message
            print("HTTPError Code {}: {}".format(e_dict["error"]["code"], e_dict["error"]["message"]))
            return login(e_dict["error"]["message"], False)

#Sign up function
def do_signup():
    email = request.form['u_email']
    password = request.form['u_password']
    confirm_password = request.form['u_confirm_password']

    #Check user input for password confirmation
    if password != confirm_password:
        return signup("Passwords do not match!", False)

    email_parts = email.split('@', 2)

    #Check user input for "@purdue.edu"
    if email_parts[1].casefold() != "purdue.edu":
        return signup("Email not supported!", False)

    #Check if user's career ID exists in the database
    career_id = email_parts[0]
    user_ref = firestore_database.collection('users').document(career_id)

    if user_ref.get().exists:
        print("User {} already exists!".format(user_ref.get().to_dict()))
        return signup("The email {} has already been used.".format(email), False)
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
            return signup(e_dict["error"]["message"], False)
        except Exception as e:
            print("Authentication or Database FAILURE - {}".format(e))
            return signup("Authentication or Database FAILURE", False)
