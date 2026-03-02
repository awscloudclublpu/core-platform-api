import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("creds/firebase/firebase-service-account.json")

firebaseApp = firebase_admin.initialize_app(cred)