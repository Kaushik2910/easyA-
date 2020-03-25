from flask import Flask, session
from flask_mail import Mail
from flask import render_template

def create_app(test_config=None):
    #Create the Flask application and its blueprints
    app = Flask(__name__)
    mail = Mail(app)
    app.secret_key = 'any random'


    #Check if debugging config was included
    if test_config is None:
        app.config.from_object('config')
    else:
        app.config.from_mapping(test_config)

    return app, mail


app, mail = create_app()
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pratyakshmotwani99@gmail.com'  # enter your email here
app.config['MAIL_DEFAULT_SENDER'] = 'pratyakshmotwani99@gmail.com' # enter your email here
app.config['MAIL_PASSWORD'] = 'pratsandrishu' # enter your password here

#Render the pages in views.py
import easyA.views

#import easyA.auth