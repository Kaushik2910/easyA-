import pyrebase
from google.cloud import firestore
import firebase_admin 
import firebase_admin.auth as admin_auth
import os

def init_db():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(os.path.abspath('easyA/instance/dbauth.json'))
    firestore_database = firestore.Client()
    admin = firebase_admin.initialize_app()

    config = {
        "apiKey": "AIzaSyCKndXyjPiRqsEWRveZNfSI_-wAC7ZU3EI",
        "authDomain": "easya-b1ec1.firebaseapp.com",
        "databaseURL": "https://easya-b1ec1.firebaseio.com",
        "projectId": "easya-b1ec1",
        "storageBucket": "easya-b1ec1.appspot.com",
    }

    firebase_wrapper = pyrebase.initialize_app(config)
    realtime_database = firebase_wrapper.database()

    return firestore_database, realtime_database, firebase_wrapper, admin_auth