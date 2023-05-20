import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from utils.utils import *

import json
import os

MAX_BATCH_SIZE = 500
CREDENTIAL_PATH = 'busyBody_serviceAccount.json'


def push_to_firestore(db, data, collection_name):
    batch = db.batch()
    for index, d in enumerate(data):
        ref = db.collection(collection_name).document()
        if index != 0 and index % MAX_BATCH_SIZE == 0:
            batch.commit()
        batch.set(ref, d)
    batch.commit()  # for remaining items


if __name__ == "__main__":
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIAL_PATH
    cred = credentials.Certificate(CREDENTIAL_PATH)
    app = firebase_admin.initialize_app()
    firestore_db = firestore.client()

    # exercise_data = getJsonData('../Data/workouts.json')
    # pushToFirestore(firestore_db, exercise_data, 'workouts')

    # recipe_data = load_json('../Data/recipes.json')
    # push_to_firestore(firestore_db, recipe_data, 'recipes')

    yelp_data = load_json('../Data/yelpSimple.json')
    push_to_firestore(firestore_db, yelp_data, 'restaurants')
