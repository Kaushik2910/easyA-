from easyA import app, mail
from easyA import db


from flask import render_template, request, session, redirect, url_for
from flask_mail import Message
from googletrans import Translator
import os
import google.cloud
from lxml import html
import requests
import json
import time
import datetime
import operator

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
            session['errorMessage'] = "You cannot contact the reviewer because you are BANNED!"
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
def course_page(course_id, get_info=False, errorMessage=""):
        if 'errorMessage' in session:
            errorMessage = session['errorMessage']
            session.pop('errorMessage')
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

                    #Check if Prof is in rate my prof
                    page_uri = "https://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&queryBy=teacherName&schoolName=Purdue+University+-+West+Lafayette&schoolID=783&query=" + tempDict['professor'].replace(" ", "+")
                    page = requests.get(page_uri)
                    tree = html.fromstring(page.content)
                    result = tree.xpath('//div[@class="result-count"]/text()')[2]
                    if result == "Your search didn\'t return any results.":
                        tempDict['professor_link'] = ""
                        result_count = 0
                    else:
                        result_count = int(result.split(" ")[3])

                    if result_count == 1:
                        professor_page = "https://www.ratemyprofessors.com" + tree.xpath('//li[@class="listing PROFESSOR"]/a/@href')[0]
                        tempDict['professor_link'] = professor_page
                    elif result_count > 1:
                        tempDict['professor_link'] = page_uri

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

                    #Check if Prof is in rate my prof
                    page_uri = "https://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&queryBy=teacherName&schoolName=Purdue+University+-+West+Lafayette&schoolID=783&query=" + tempDict['professor'].replace(" ", "+")
                    page = requests.get(page_uri)
                    tree = html.fromstring(page.content)
                    result = tree.xpath('//div[@class="result-count"]/text()')[2]
                    if result == "Your search didn\'t return any results.":
                        tempDict['professor_link'] = ""
                        result_count = 0
                    else:
                        result_count = int(result.split(" ")[3])

                    if result_count == 1:
                        professor_page = "https://www.ratemyprofessors.com" + tree.xpath('//li[@class="listing PROFESSOR"]/a/@href')[0]
                        tempDict['professor_link'] = professor_page
                    elif result_count > 1:
                        tempDict['professor_link'] = page_uri

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

        return render_template('course.html', course_id=course_id, course_name=course_name, description=description, rating=rating, rating_count=rating_count, posts=sorted_posts, user_posts=user_posts, current_profs=current_profs, current_tags=current_tags, upvoted=upvoted, downvoted=downvoted, sort_value=sort_function, course_list=course_list, errorMessage=errorMessage)

@app.route('/course/<course_id>/<post_id>', methods=['POST', 'GET'])
def review_reports(course_id, post_id):
    #Only admins allowed here

    if 'email' not in session:
        return render_template("not_found.html")

    if 'group' not in session or session['group'] != "admin":
        return render_template("not_found.html")

    # career_id = (session['email'].split('@', 2))[0]
    # user = firestore_database.collection('users').document(career_id).get()
    course_ref = firestore_database.collection('courses').where('course_id', '==', course_id)

    post = firestore_database.collection('posts').document(post_id).get()
    postDict = dict()
    reports = []
    for course in course_ref.stream():
        if post.exists and post.to_dict()['course'] == course.reference:
            postDict = post.to_dict()
            postDict['post_ID'] = post.id
            postDict['author'] = postDict['author'].get().id
            postDict['course'] = postDict['course'].get().to_dict()['course_id']
            report_ref = firestore_database.collection('reports').where('report_post', '==', post.reference).stream()
            for report in report_ref:
                tempDict = report.to_dict()
                tempDict['report_ID'] = report.id
                tempDict['author'] = tempDict['author'].get().id
                reports.append(tempDict)
        else:
            return render_template("not_found.html")

    return render_template('review_reports.html', post=postDict, reports=reports)

#Deleting a report function
@app.route('/delete_report_admin', methods=['POST', 'GET'])
def delete_report_admin():
    #Check for logged in or not
    if 'email' not in session:
        return render_template("not_found.html")

    if 'group' not in session or session['group'] != "admin":
        return render_template("not_found.html")

    if request.method == 'POST':
        report = firestore_database.collection('reports').document(request.form['report_ID']).get()
        post = firestore_database.collection('posts').document(request.form['post_ID']).get()

        report_count = int(post.to_dict()['report_count']) - 1
        post.reference.update({
            "report_count": int(report_count)
        })

        #Delete post
        report.reference.delete()

        return redirect(request.environ['HTTP_REFERER'])

    return render_template("not_found.html")


@app.route('/course/<course_id>/new_review', methods=['POST', 'GET'])
def new_review(course_id):
    if 'email' not in session:
        return login("Please login to post reviews!", False)

    #Banned user
    if session['group'] == "banned":
        session['errorMessage'] = "You cannot add a new post because you are BANNED!"
        return redirect("/course/" + course_id)

    professors = []
    course, course_id, course_name, user_posts = course_page(course_id, True)
    if len(user_posts) > 0:
        #User has already posted a review, do not post render new review page

        #TODO: Show error in course page
        session['errorMessage'] = "You already have a review on this course!"
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
            session['errorMessage'] = "You cannot report a post because you are BANNED!"
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
    author_dict = author.to_dict()
    added_professors = []
    if 'added_professors' in author_dict:
        if author.to_dict()['added_professors'] != "[]":
            added_professors = author.to_dict()['added_professors'].strip("[]").replace('\'', '').split(", ")
            count_profs = 0
            temp_add_prof = added_professors.copy()
            for p in added_professors:
                p_ref = firestore_database.collection('professors').document(p)
                if not p_ref.get().exists:
                    #If professor was delete from database, either by ref count or an admin
                    temp_add_prof.remove(p)
                    continue
                p_dict = p_ref.get().to_dict()
                if p_dict['course'].get().to_dict()['course_id'] == course_id:
                    if p_dict['professor_name'] != request.form['professor']:
                        count_profs = count_profs + 1
            added_professors = temp_add_prof
            if count_profs >= 5:
                #TODO: add error that user already has an added professor

                session['errorMessage'] = "You added new five professors to this course, please use an existing professor name!"
                return redirect('/course/' + str(course_id))
    
    #Check if professor is in database or not
    professor_ref = firestore_database.collection('professors').where('professor_name', '==', request.form['professor'])
    prof_exists = None
    for professor in professor_ref.stream():
        prof_exists = professor

    if not prof_exists:
        #Add to database
        prof_data = {
            "course": course.reference,
            "professor_name": request.form['professor'],
            "reference_count": 1
        }
        firestore_database.collection('professors').add(prof_data)

        #Link to user
        for professor in professor_ref.stream():
            prof_exists = professor

        added_professors.append(prof_exists.id)
    else:
        #Incerement ref. count
        prof_exists.reference.update({
                "reference_count": prof_exists.to_dict()['reference_count'] + 1
        })

    data = {
        "posted_date": datetime.datetime.now().isoformat(),
        "author": author.reference,
        "course": course.reference,
        "course_id":request.form['course'],
        "professor": request.form['professor'],
        "attendance": request.form['attendance'],
        "textbook": request.form['textbook'],
        "semester_taken": str(request.form['semester_taken']) + " " + str(request.form['semester_taken_year']) if str(request.form['semester_taken']) != "" else "",
        "grade": request.form['grade'],
        "rating": int(request.form['rating']) if request.form['rating'] else 1,
        "tags": request.form['tags'],
        "text": request.form['text'],
        "report_count": 0,
        "downvotes": 0,
        "upvotes": 0,
        "translated_text" : str("")
    }

    #Add the post to the database
    firestore_database.collection('posts').add(data)

    #Update the added_professors array if necessary
    author.reference.update({
        "added_professors": str(added_professors)
    })

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
            session['errorMessage'] = "You cannot delete a post because you are BANNED!"
            return redirect(request.environ['HTTP_REFERER'])

        career_id = (session['email'].split('@', 2))[0]
        author = firestore_database.collection('users').document(career_id).get()
        post = firestore_database.collection('posts').document(request.form['post_ID']).get()
        post_dict = post.to_dict()
        professor_ref = firestore_database.collection('professors').where('professor_name', '==', post_dict['professor'])
        for professor in professor_ref.stream():
            prof_exists = professor

        #Make sure the user owns the post
        if post_dict['author'] != author.reference and not ('group' in session and session['group'] == "admin"):

            #TODO: Show error that user cannot delete this post
            session['errorMessage'] = "You cannot delete a post that is not yours!"
            return redirect('/course/' + str(post_dict['course'].get().to_dict()['course_id']))


        #Delete all related reports
        report_ref = firestore_database.collection('reports').where('report_post', '==', post.reference).stream()
        for report in report_ref:
            report.reference.delete()

        #Decrement professor reference count
        prof_exists.reference.update({
                "reference_count": int(prof_exists.to_dict()['reference_count']) - 1
        })

        #Delete post
        post.reference.delete()

        if int(prof_exists.reference.get().to_dict()['reference_count']) <= 0:
            #Delete professor because ref count is 0
            prof_exists.reference.delete()

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
            session['errorMessage'] = "You cannot upvote a post because you are BANNED!"
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
            session['errorMessage'] = "You cannot downvote a post because you are BANNED!"
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


@app.route('/translate_text',methods=['POST', 'GET'])
def do_translate_text():

    translator = Translator()

    post = firestore_database.collection('posts').document(request.form['post_ID']).get()

    post_dict = post.to_dict()

    if post_dict['translated_text']:

        post.reference.update({
                "translated_text": str("")
        })

    else:
        result = translator.translate(post_dict['text'])

        transalated_txt = result.text

        post.reference.update({
                "translated_text": str(transalated_txt)
        })

    return redirect('/course/' + str(post_dict['course'].get().to_dict()['course_id']))
