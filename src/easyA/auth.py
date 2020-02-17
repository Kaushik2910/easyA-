from flask import request, render_template
from easyA import db
from easyA import app

db, pyrebase = db.init_db()
auth = pyrebase.auth()

@app.route('/api/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        data = {
            "email": email,
            "password": password
        }

        user_exists = 1

        all_users = db.child("users").get()

        try:
            user = all_users[email]
        except:
            user_exists = 0
        
        # Check if user already exists

        if user_exists == 1:
            return 'User already exists'
        else :
            try:
                auth.create_user_with_email_and_password(email, password)
                user = auth.sign_in_with_email_and_password(email, password)
                db.child("users").push(data, user['idToken'])

                return 'Signup and Login Succesful'
            except:
                 return 'Some problem occured, try again!'          
    
    return render_template('home.html')


@app.route('/api/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            return 'Login Successful'
        except:
            return 'Please Check your Credentials!'
    
    return render_template('home.html')