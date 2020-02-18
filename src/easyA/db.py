import pyrebase
from google.cloud import firestore
import os

def init_db():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(os.path.abspath('easyA/instance/dbauth.json'))
    firestore_database = firestore.Client()

    config = {
        "apiKey": "AIzaSyCKndXyjPiRqsEWRveZNfSI_-wAC7ZU3EI",
        "authDomain": "easya-b1ec1.firebaseapp.com",
        "databaseURL": "https://easya-b1ec1.firebaseio.com",
        "projectId": "easya-b1ec1",
        "storageBucket": "easya-b1ec1.appspot.com",
    }

    firebase_wrapper = pyrebase.initialize_app(config)
    realtime_database = firebase_wrapper.database()

    return firestore_database, realtime_database, firebase_wrapper