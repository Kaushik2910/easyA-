from flask import Flask
from flask import render_template

def create_app(test_config=None):
    #Create the Flask application and its blueprints
    app = Flask(__name__)

    #Check if debugging config was included
    if test_config is None:
        app.config.from_object('config')
    else:
        app.config.from_mapping(test_config)

    return app


app = create_app()

#Render the pages in views.py
import easyA.views

#import easyA.auth
