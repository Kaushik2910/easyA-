import pyrebase

config = {
  "apiKey": "AIzaSyCKndXyjPiRqsEWRveZNfSI_-wAC7ZU3EI",
  "databaseURL": "https://easya-b1ec1.firebaseio.com",
  "projectId": "easya-b1ec1",
  "serviceAccount": "easyA/instance/firebase-private-key.json",
}

firebase = pyrebase.initialize.app(config)
db = firebase.database()

