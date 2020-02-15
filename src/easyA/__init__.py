from flask import Flask
from flask import render_template
from easyA.views import views_app

def create_app(test_config=None):
    #Create the Flask application and its blueprints
    app = Flask(__name__)

    #Render the pages in views.py
    app.register_blueprint(views_app)

    #Connect to the database
    from . import db
    db.init_db()

    #Check if debugging config was included
    if test_config is None:
        app.config.from_object('config')
    else:
        app.config.from_mapping(test_config)

    return app


app = create_app()
