from google.cloud import firestore
import os

def init_db():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(os.path.abspath("instance/dbauth.json"))

    firestore_database = firestore.Client()

    pyrebase_config = {
      "apiKey": "AIzaSyCKndXyjPiRqsEWRveZNfSI_-wAC7ZU3EI",
      "authDomain": "easya-b1ec1.firebaseapp.com",
      "databaseURL": "https://easya-b1ec1.firebaseio.com",
       "projectId": "easya-b1ec1",
       "storageBucket": "easya-b1ec1.appspot.com",
    }

    pyrebase = pyrebase.initialize_app(config)

    return database