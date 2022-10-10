from flask import Flask, jsonify, request, g
from flask_cors import CORS
import pymongo, json, requests, os
from bson.json_util import dumps
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import seed
load_dotenv()

db = os.environ.get("MONGODB_URI")

DEBUG = True
PORT = os.environ.get("PORT")

app = Flask(__name__)
client = pymongo.MongoClient(db)
  
# Database
Database = client.get_database('knockknock')
# Table
jokes = Database.jokes


def parse_json(data):
	return json.loads(dumps(data))

def query(payload):
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = ''
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# routes here 

# Get all jokes
@app.route('/jokes', methods=['GET'])
def find():
	thing = jokes.find({})
	return parse_json(thing)

# seed stuff
# Don't run this unless it's to reset the database lmao
# @app.route('/seed', methods=['GET'])
# def seeding():
#     for joke in seed.jokes:
#         def seedJokes(joke):
#             queryObject = {
#                 'user': 'Tim',
#                 'setup': joke["name"],
# 		        'punchline': joke["punch"]
#             }
#             query = jokes.insert_one(queryObject)
#             return "Joke Added to Database"
#         seedJokes(joke)


# testing hugging face sentence transformer
@app.route('/test', methods=['GET'])

def dothething():
    testVal = "who"
    sents = [
			"what",
			"who",
			"owl"
		]
    output = query({
	"inputs": {
		"source_sentence": testVal,
		"sentences": sents
	    },
    })
    mostSimilar = max(output)*100
    if mostSimilar < 50:
        return "I'm not sure about that..."
    print(sents[output.index(mostSimilar)], mostSimilar)
    return output

# get setup from db test
@app.route('/setup', methods=['GET'])

def setup():
    sents = jokes.find({},{"setup": 1, "_id":0})
    return parse_json(sents.values())

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