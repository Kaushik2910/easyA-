from flask import Flask
from flask import render_template

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_object('config')
    else:
        app.config.from_mapping(test_config)

    from . import db
    db.init_db()

    return app


app = create_app()

@app.route('/')
def index():
    return render_template('home.html')

