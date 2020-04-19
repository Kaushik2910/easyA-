from easyA import app, mail
from easyA import db


from flask import render_template, request, session, redirect, url_for
from flask_mail import Message
from googletrans import Translator
import google.cloud
import requests
import json
import time
import datetime
import operator
import pyttsx3

firestore_database, realtime_database, firebase_wrapper, admin_auth = db.init_db()
auth = firebase_wrapper.auth()

@app.route('/')
def index(get_info=False):
    courses_ref = firestore_database.collection('courses').stream()
    course_list = []
    for course in courses_ref:
        post_ref = firestore_database.collection('posts').where('course', '==', course.reference).stream()
        tempDict = course.to_dict()
        tempDict['post_count'] = 0
        for post in post_ref:
            tempDict['post_count'] = tempDict['post_count'] + 1

        course_list.append(tempDict)

    if get_info:
        return course_list

    return render_template('home.html', course_list=course_list)

@app.errorhandler(404)
def not_found(e):
  return render_template("not_found.html")

# @app.route('/contact_us')
# def contact_us():
#     return render_template('contact_us.html')

# App route for contact page
@app.route('/contact', methods=['POST', 'GET'])
def contact():
    #Check for logged in or not
    if 'email' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        #Banned user
        if session['group'] == "banned":
            return redirect(request.environ['HTTP_REFERER'])

        post = firestore_database.collection('posts').document(request.form['post_ID']).get()
        return render_template('contact.html', post_ID=request.form['post_ID'], post=post.to_dict())

    return redirect(url_for('index'))

@app.route('/reset_pwd', methods=['POST', 'GET'])
def reset_pwd(errorMessage="", requestTrigger=True):
    if 'email' not in session:
        return redirect(url_for('index'))
    if (request.method == 'POST') and requestTrigger:
        return do_change_password()

    return render_template('reset_pwd.html', errorMessage=errorMessage)

@app.route('/forgot_pwd', methods=['POST', 'GET'])
def forgot_pwd(errorMessage="", requestTrigger=True):
    if (request.method == 'POST' and requestTrigger):
        return do_password_reset()

    return render_template('forgot_pwd.html', errorMessage=errorMessage)

@app.route('/signout')
def signout():
    session.pop('email', None)
    session.pop('group', None)
    return redirect(request.environ['HTTP_REFERER'])

@app.route('/login', methods=['POST', 'GET'])
def login(errorMessage="", requestTrigger=True):
    if 'email' in session:
        return redirect(url_for('index'))

    if (request.method == 'POST') and requestTrigger:
        return do_login()
    return render_template('login.html', errorMessage=errorMessage)

@app.route('/signup', methods=['POST', 'GET'])
def signup(errorMessage="", requestTrigger=True):
    if 'email' in session:
        return redirect(url_for('index'))

    if (request.method == 'POST') and requestTrigger:
        return do_signup()
    return render_template('signup.html', errorMessage=errorMessage)

# App route for contact adminstrator page
@app.route('/contact_admin', methods=['POST', 'GET'])
def contact_admin():
    return render_template('contact_us.html')

@app.route( '/course/')
@app.route('/course/<course_id>', methods=['POST', 'GET'])
def course_page(course_id, get_info=False):

        course_name = ""
        posts = []
        user_posts = []
        current_profs = []
        current_tags = []
        upvoted = []
        downvoted = []
        courses_ref = firestore_database.collection('courses').where('course_id', '==', course_id)

        #Check how many posts the user has
        if 'email' in session:
            career_id = (session['email'].split('@', 2))[0]
            user = firestore_database.collection('users').document(career_id).get()

            if 'upvoted' in user.to_dict():
                #Grab array of upvoted posts
                if user.to_dict()['upvoted'] != "[]":
                    upvoted = user.to_dict()['upvoted'].strip("[]").replace('\'', '').split(", ")

            if 'downvoted' in user.to_dict():
                #Grab array of downvoted posts
                if user.to_dict()['downvoted'] != "[]":
                    downvoted = user.to_dict()['downvoted'].strip("[]").replace('\'', '').split(", ")

        for course in courses_ref.stream():
            course_dic = course.to_dict()
            course_id = course_dic['course_id']
            course_name = course_dic['course_name']
            description = course_dic['description']
            rating = 0
            rating_count = 0
            post_ref = firestore_database.collection('posts').where('course', '==', course.reference).stream()
            if 'group' in session and session['group'] == "admin":
                for post in post_ref:
                    tempDict = post.to_dict()
                    tempDict['author'] = tempDict['author'].get().id
                    tempDict['post_ID'] = post.id

                    #Sum all course rating
                    rating += tempDict['rating']
                    rating_count += 1
    
                    posts.append(tempDict)
                    #Build professors array
                    if tempDict['professor'] not in current_profs:
                        current_profs.append(tempDict['professor'])

                    #Build tags array
                    post_tags = tempDict['tags'].split(",")
                    for tag in post_tags:
                        if tag and tag not in current_profs:
                            current_tags.append(tag)
            else:
                for post in post_ref:
                    tempDict = post.to_dict()
                    tempDict['post_ID'] = post.id

                    #Sum all course rating
                    rating += tempDict['rating']
                    rating_count += 1
        

                    if tempDict['text'] and not tempDict['text'].isspace():
                        posts.append(tempDict)
                        #Build professors array
                        if tempDict['professor'] not in current_profs:
                            current_profs.append(tempDict['professor'])

                        #Build tags array
                        post_tags = tempDict['tags'].split(",")
                        for tag in post_tags:
                            if tag and tag not in current_profs:
                                current_tags.append(tag)

                    #Collect logged in user's posts
                    if 'email' in session and tempDict['author'] == user.reference:
                        user_posts.append(tempDict)

            #Calculate average rating
            if rating_count != 0:
                rating = int(rating / rating_count)
            else:
                rating = 0

        if not course_name:
            return render_template("not_found.html")

        if get_info:
            return course, course_id, course_name, user_posts

        #Sort posts

        #Sort posts chronologically -- default
        sorted_posts = sorted(posts, key = lambda i: (time.mktime(datetime.datetime.strptime(i['posted_date'][:19], "%Y-%m-%dT%H:%M:%S").timetuple())))

        if request.method == 'POST':
            sort_function = request.form['sort']
        elif 'sort' in session:
            sort_function = session.pop('sort', None)
        else:
            sort_function = "chronological_old"

        if sort_function == 'most_upvotes':
            sorted_posts = sorted(sorted_posts, key = lambda i: (i['upvotes']), reverse=True)
        elif sort_function == 'least_upvotes':
            sorted_posts = sorted(sorted_posts, key = lambda i: (i['upvotes']))
        elif sort_function == 'chronological_new':
            sorted_posts = sorted(posts, key = lambda i: (time.mktime(datetime.datetime.strptime(i['posted_date'][:19], "%Y-%m-%dT%H:%M:%S").timetuple())), reverse=True)
        elif sort_function == 'chronological_old':
            sorted_posts = sorted(posts, key = lambda i: (time.mktime(datetime.datetime.strptime(i['posted_date'][:19], "%Y-%m-%dT%H:%M:%S").timetuple())))

        #Get the course list and post count from the index function
        course_list = index(get_info=True)

        return render_template('course.html', course_id=course_id, course_name=course_name, description=description, rating=rating, rating_count=rating_count, posts=sorted_posts, user_posts=user_posts, current_profs=current_profs, current_tags=current_tags, upvoted=upvoted, downvoted=downvoted, sort_value=sort_function, course_list=course_list)

@app.route('/course/<course_id>/new_review', methods=['POST', 'GET'])
def new_review(course_id):
    if 'email' not in session:
        return login("Please login to post reviews!", False)

    #Banned user
    if session['group'] == "banned":
        return redirect("/course/" + course_id)

    professors = []
    course, course_id, course_name, user_posts = course_page(course_id, True)
    if len(user_posts) > 0:
        #User has already posted a review, do not post render new review page

        #TODO: Show error in course page

        return redirect('/course/' + course_id)

    if request.method == 'POST':
        return post_review(course, course_id)

    professor_ref = firestore_database.collection('professors').where('course', '==', course.reference).stream()
    for professor in professor_ref:
        professors.append(professor.to_dict())


    return render_template('new_review.html', course_id=course_id, course_name=course_name, professors=professors)

@app.route('/report', methods=['POST', 'GET'])
def report():
    #Check for logged in or not
    if 'email' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        #Banned user
        if session['group'] == "banned":
            return redirect(request.environ['HTTP_REFERER'])
        
        post = firestore_database.collection('posts').document(request.form['post_ID']).get()
        return render_template('report.html', post_ID=request.form['post_ID'], post=post.to_dict())

    return redirect(url_for('index'))

#Posting a report function
@app.route('/post_report', methods=['POST', 'GET'])
def post_report():
    if request.method == 'POST':
        career_id = (session['email'].split('@', 2))[0]
        author = firestore_database.collection('users').document(career_id).get()
        post = firestore_database.collection('posts').document(request.form['post_ID']).get()
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

        if report_count > 5:
            message_body = "The report count for the post exceeded the specified limit:\n\n" + "Post ID: " + request.form['post_ID']
            msg = Message(body=message_body, subject="Admin: Post report limit exceeded!!!", recipients=['easyApurdue@gmail.com'])
            mail.send(msg)

        #Add the report to the database
        firestore_database.collection('reports').add(data)

        return redirect('/course/' + str(post.to_dict()['course'].get().to_dict()['course_id']))

    return redirect(url_for('index'))

@app.route('/post_contact', methods=['POST', 'GET'])
def post_contact():

    if request.method == 'POST':

        post = firestore_database.collection('posts').document(request.form['post_ID']).get()

        post_dict = post.to_dict()
        author_dict = post_dict['author'].get().to_dict()
        author_email = author_dict['email']
        user_email = session['email']

        message = request.form['message']
        subject = request.form['subject']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        name = first_name + " " + last_name
        message_body = "A user sent you the following message:\n\n" + "Name: " + name + "\nSubject: " + subject + "\nMeassage: " + message + "\nSent by: " + user_email

        msg = Message(body=message_body, subject="easyA: Someone would like to contact you!", recipients=[author_email])
        mail.send(msg)

        return redirect('/course/' + str(post.to_dict()['course'].get().to_dict()['course_id']))

    return redirect(url_for('index'))

@app.route('/post_contact_admin', methods=['POST', 'GET'])
def post_contact_admin():

    if request.method == 'POST':

        user_email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        message_body = "A user sent you the following message:\n\n" + "Subject: " + subject + "\nMeassage: " + message

        if user_email == "":
            data = {
                "subject": subject,
                "message": message,
            }
        else:
            data = {
                "email": user_email,
                "subject": subject,
                "message": message,
            }
            message_body += "\nSent by: " + user_email

        #Add the inquiry to the database
        firestore_database.collection('inquiries').add(data)
        
        # Send mail
        msg = Message(body=message_body, subject="Admin: A user wants to contact you", recipients=['easyApurdue@gmail.com'])
        mail.send(msg)

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
        "semester_taken": str(request.form['semester_taken']) + " " + str(request.form['semester_taken_year']) if str(request.form['semester_taken']) != "Prefer not to mention" else "",
        "grade": request.form['grade'],
        "rating": int(request.form['rating']) if request.form['rating'] else 1,
        "tags": request.form['tags'],
        "text": request.form['text'],
        "report_count": 0,
        "downvotes": 0,
        "upvotes": 0
    }

    #Add the post to the database
    firestore_database.collection('posts').add(data)

    return redirect('/course/' + str(course_id))

#Deleting a review function
@app.route('/delete_review', methods=['POST', 'GET'])
def delete_review():
    #Check for logged in or not
    if 'email' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        #Banned user
        if session['group'] == "banned":
            return redirect(request.environ['HTTP_REFERER'])
        
        career_id = (session['email'].split('@', 2))[0]
        author = firestore_database.collection('users').document(career_id).get()
        post = firestore_database.collection('posts').document(request.form['post_ID']).get()
        post_dict = post.to_dict()

        #Make sure the user owns the post
        if post_dict['author'] != author.reference and not ('group' in session and session['group'] == "admin"):

            #TODO: Show error that user cannot delete this post

            return redirect('/course/' + str(post_dict['course'].get().to_dict()['course_id']))


        #Delete all related reports
        report_ref = firestore_database.collection('reports').where('report_post', '==', post.reference).stream()
        for report in report_ref:
            report.reference.delete()

        #Delete post
        post.reference.delete()

        return redirect('/course/' + str(post_dict['course'].get().to_dict()['course_id']))

    return redirect(url_for('index'))

#Login function
def do_login():
    email = request.form['u_email']
    password = request.form['u_password']

    try:
        pyrebase_user = auth.sign_in_with_email_and_password(email, password)
        firebase_user = admin_auth.get_user(pyrebase_user['localId'])

        if not firebase_user.email_verified:
            #Send email verification
            auth.send_email_verification(pyrebase_user['idToken'])

            return login("Email is not verified! Please verify your email!", False)

        session['email'] = email
        career_id = email.split('@', 2)[0]
        user_ref = firestore_database.collection('users').document(career_id)
        user_dict =  user_ref.get().to_dict()

        if 'group' not in user_dict:
            #Add the group to the user if doesn't have a group
            user_ref.update({
                "group": "student",
            })

        user_dict =  user_ref.get().to_dict()
        session['group'] = user_dict['group']
        

        print("User logged in successfully")
        return redirect(request.environ['HTTP_REFERER'])
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
            auth.create_user_with_email_and_password(email, password)

            #Record the user in the database
            data = {
                "email": email,
                "group": "student"
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

#Change password function
def do_change_password():
    password = request.form['u_password']
    new_password = request.form['u_new_password']
    confirm_password = request.form['u_confirm_password']

    #Check user input for password confirmation
    if new_password != confirm_password:
        return reset_pwd("Passwords do not match!", False)

    try:
        pyrebase_user = auth.sign_in_with_email_and_password(session['email'], password)
        admin_auth.update_user(pyrebase_user['localId'], password=new_password)
        return reset_pwd("Password changed succussfully!", False)
    except requests.exceptions.HTTPError as e:
        #Create a dictionary from the error
        e_dict = json.loads(e.strerror)

        #Check if a credentials error occured
        if e_dict["error"]["message"] == "INVALID_PASSWORD" or e_dict["error"]["message"] == "EMAIL_NOT_FOUND":
            return reset_pwd("Please enter the correct old password!", False)
        else:
            #Print error code and message
            print("HTTPError Code {}: {}".format(e_dict["error"]["code"], e_dict["error"]["message"]))
            return reset_pwd(e_dict["error"]["message"], False)

def do_password_reset():
    email = request.form['u_email']
    print("Email for Password Reset: ", email)

    try:
        # Send Password Reset email
        auth.send_password_reset_email(email)
        return forgot_pwd('Password Reset Email Sent!', False)
    except requests.exceptions.HTTPError as e:
        #Create a dictionary from the error
        e_dict = json.loads(e.strerror)

        #Check if a credentials error occured
        if e_dict["error"]["message"] == "EMAIL_NOT_FOUND":
            return forgot_pwd("Email is not registed!", False)
        else:
            #Print error code and message
            print("HTTPError Code {}: {}".format(e_dict["error"]["code"], e_dict["error"]["message"]))
            return forgot_pwd(e_dict["error"]["message"], False)

@app.route('/upvote', methods=['POST', 'GET'])
def do_upvote():
    if request.method == 'POST':
        #Banned user
        if session['group'] == "banned":
            return redirect(request.environ['HTTP_REFERER'])
        
        career_id = (session['email'].split('@', 2))[0]
        author = firestore_database.collection('users').document(career_id).get()

        post = firestore_database.collection('posts').document(request.form['post_ID']).get()
        post_dict = post.to_dict()

        #Check for logged in or not
        if 'email' not in session:
            return redirect('/course/' + str(post_dict['course'].get().to_dict()['course_id']))

        upvoted = []
        downvoted = []

        if 'upvoted' in author.to_dict():
            #Grab array of upvoted posts
            if author.to_dict()['upvoted'] != "[]":
                upvoted = author.to_dict()['upvoted'].strip("[]").replace('\'', '').split(", ")


        if 'downvoted' in author.to_dict():
            #Grab array of downvoted posts
            if author.to_dict()['downvoted'] != "[]":
                downvoted = author.to_dict()['downvoted'].strip("[]").replace('\'', '').split(", ")

        if request.form['post_ID'] in upvoted:
            #Undo upvote
            upvotes = post.to_dict()['upvotes'] - 1

            upvoted.remove(request.form['post_ID'])

            #Update database
            author.reference.update({
                "upvoted": str(upvoted),
            })
        elif request.form['post_ID'] in downvoted:
            #Switch from downvotes to upvotes

            upvotes = post.to_dict()['upvotes'] + 1

            downvotes = post.to_dict()['downvotes'] - 1

            downvoted.remove(request.form['post_ID'])
            upvoted.append(request.form['post_ID'])

            #Update database
            author.reference.update({
                "upvoted": str(upvoted),
                "downvoted": str(downvoted)
            })

            post.reference.update({
            "downvotes": int(downvotes)
            })
        else:
            #Include in upvote array
            upvoted.append(request.form['post_ID'])

            #Upvote
            upvotes = post.to_dict()['upvotes'] + 1

            #Update database
            author.reference.update({
                "upvoted": str(upvoted),
            })


        post.reference.update({
            "upvotes": int(upvotes)
        })

        session['sort'] = request.form['sort']
        return redirect('/course/' + str(post_dict['course'].get().to_dict()['course_id']))
    return redirect(url_for('index'))

@app.route('/downvote', methods=['POST', 'GET'])
def do_downvote():
    if request.method == 'POST':
        #Banned user
        if session['group'] == "banned":
            return redirect(request.environ['HTTP_REFERER'])
        
        post = firestore_database.collection('posts').document(request.form['post_ID']).get()
        post_dict = post.to_dict()

        #Check for logged in or not
        if 'email' not in session:
            return redirect('/course/' + str(post_dict['course'].get().to_dict()['course_id']))

        career_id = (session['email'].split('@', 2))[0]
        author = firestore_database.collection('users').document(career_id).get()

        upvoted = []
        downvoted = []

        if 'upvoted' in author.to_dict():
            #Grab array of upvoted posts
            if author.to_dict()['upvoted'] != "[]":
                upvoted = author.to_dict()['upvoted'].strip("[]").replace('\'', '').split(", ")


        if 'downvoted' in author.to_dict():
            #Grab array of downvoted posts
            if author.to_dict()['downvoted'] != "[]":
                downvoted = author.to_dict()['downvoted'].strip("[]").replace('\'', '').split(", ")


        if request.form['post_ID'] in downvoted:
            #Undo downvote
            downvotes = post.to_dict()['downvotes'] - 1

            downvoted.remove(request.form['post_ID'])

            #Update database
            author.reference.update({
                "downvoted": str(downvoted),
            })
        elif request.form['post_ID'] in upvoted:
            #Downvote
            downvotes = post.to_dict()['downvotes'] + 1

            upvotes = post.to_dict()['upvotes'] - 1

            #Switch from upvotes to downvotes

            upvoted.remove(request.form['post_ID'])
            downvoted.append(request.form['post_ID'])

            #Update database
            author.reference.update({
                "upvoted": str(upvoted),
                "downvoted": str(downvoted)
            })

            post.reference.update({
            "upvotes": int(upvotes)
            })
        else:
            #Downvote
            downvotes = post.to_dict()['downvotes'] + 1

            #Include in downvote array
            downvoted.append(request.form['post_ID'])

            #Update database
            author.reference.update({
                "downvoted": str(downvoted),
            })


        post.reference.update({
            "downvotes": int(downvotes)
        })

        session['sort'] = request.form['sort']
        return redirect('/course/' + str(post_dict['course'].get().to_dict()['course_id']))
    return redirect(url_for('index'))

@app.route('/text_to_speech',methods=['POST', 'GET'])
def do_text_to_speech():

    engine = pyttsx3.init()

    post = firestore_database.collection('posts').document(request.form['post_ID']).get()

    post_dict = post.to_dict()
    
    engine.say(post_dict['text'])
    
    engine.runAndWait()
    
    return redirect('/course/' + str(post_dict['course'].get().to_dict()['course_id']))

@app.route('/translate_text',methods=['POST', 'GET'])
def do_translate_text():

    translator = Translator()
    
    post = firestore_database.collection('posts').document(request.form['post_ID']).get()

    post_dict = post.to_dict()

    result = translator.translate('Ciao, mi chiamo Kaushik')

    transalated_txt = result.text;

    return redirect('/course/' + str(post_dict['course'].get().to_dict()['course_id']))
