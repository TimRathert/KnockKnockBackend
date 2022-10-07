from flask import Flask, jsonify, request, g
from flask_cors import CORS
import pymongo, json
from bson.json_util import dumps
import os
from dotenv import load_dotenv

load_dotenv()

db = os.environ.get("MONGODB_URI")

DEBUG = True
PORT = 4000

app = Flask(__name__)
client = pymongo.MongoClient(db)
  
# Database
Database = client.get_database('knockknock')
# Table
jokes = Database.jokes

def parse_json(data):
	return json.loads(dumps(data))

# routes here 

# Get all jokes
@app.route('/jokes', methods=['GET'])
def find():
	thing = jokes.find({})
	return parse_json(thing)
	



# Insert new joke
@app.route('/insert-one/<setup>/<punchline>/', methods=['GET'])
def insertOne(setup, punchline):
    queryObject = {
        'user': 'Tim',
        'setup': setup,
		'punchline': punchline
    }
    query = jokes.insert_one(queryObject)
    return "Joke Added to Database"

if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)