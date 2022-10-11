from flask import Flask, jsonify, request, g, Response
from flask_cors import CORS
import pymongo, json, os, asyncio
from bson.json_util import dumps
from dotenv import load_dotenv
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
    HF_API = os.environ.get('HF_API')
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"{ HF_API }"}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

async def getAllSetups():
    return jokes.distinct('setup')

async def findPunchline(var):
    output = jokes.find({'setup': var})
    return parse_json(output)[0]
# routes here 

@app.route('/', methods=['GET'])
def home_view():
    return "<h1>Hello World!</h1>"

# Get all jokes
@app.route('/jokes', methods=['GET'])
def find():
	thing = jokes.find({})
	return parse_json(thing)

# testing hugging face sentence transformer
@app.route('/test/<setupInput>', methods=['GET'])
async def dothething(setupInput):
    sents = await getAllSetups()
    output = query({
	"inputs": {
		"source_sentence": setupInput,
		"sentences": sents
	    },
    })
    mostSimilar = max(output)
    #if mostSimilar < .50:
    #    return "I'm not sure about that..."
    jokeReturn = await findPunchline(sents[output.index(mostSimilar)])
    setup = jokeReturn['setup']
    punchline = jokeReturn['punchline']
    #print (sents[output.index(mostSimilar)],jokeReturn, mostSimilar*100)
    return f"I am {int(mostSimilar * 100)}% sure you meant {setup} and I already know that joke... {punchline}"

# receive data
@app.route('/receive', methods=['POST'])
def setup():
    data = request.form
    return (data['setup'])
# this receives data in form-data

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

if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)