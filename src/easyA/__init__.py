from flask import Flask, session
from flask_mail import Mail
from flask import render_template

def create_app(test_config=None):
    #Create the Flask application and its blueprints
    app = Flask(__name__)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'easyApurdue@gmail.com'  # enter your email here
    app.config['MAIL_DEFAULT_SENDER'] = 'easyApurdue@gmail.com' # enter your email here
    app.config['MAIL_PASSWORD'] = 'Password**1' # enter your password here

    mail = Mail(app)

    app.secret_key = 'any random'


    #Check if debugging config was included
    if test_config is None:
        app.config.from_object('config')
    else:
        app.config.from_mapping(test_config)

    return app, mail


app, mail = create_app()

#Render the pages in views.py
import easyA.views

#import easyA.auth