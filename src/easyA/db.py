import pyrebase

def init_db():

    config = {
      "apiKey": "AIzaSyCKndXyjPiRqsEWRveZNfSI_-wAC7ZU3EI",
      "authDomain": "easya-b1ec1.firebaseapp.com",
      "databaseURL": "https://easya-b1ec1.firebaseio.com",
      "projectId": "easya-b1ec1",
      "storageBucket": "easya-b1ec1.appspot.com",
      "serviceAccount": "./instance/firebase-private-key.json",
    }

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

