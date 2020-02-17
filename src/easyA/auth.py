from easyA import db

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

        # Check if user already exists

        if db.child("users").contains(data):

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