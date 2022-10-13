from flask import Flask, jsonify, request, g, Response
from flask_cors import CORS, cross_origin
import pymongo, json, os, asyncio, requests
from bson.json_util import dumps
from dotenv import load_dotenv

load_dotenv()

db = os.environ.get("MONGODB_URI")

DEBUG = True
PORT = os.environ.get("PORT")

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
client = pymongo.MongoClient(db)
  
# Database
Database = client.get_database('knockknock')
# Table
jokes = Database.jokes


def parse_json(data):
	return json.loads(dumps(data))

async def query(payload):
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

# receive data


@app.route('/', methods=['GET'])
def home_view():
    return "<h1>Hello World!</h1>"

@app.route('/receive', methods=['GET', 'POST'])
#@cross_origin() #what is this? it enables cors for all domains on this route
async def setup():
    data = request.form.get('setup')
    print(data)
    #print(request)
    return jsonify(message = data)

# Get all jokes
@app.route('/jokes', methods=['GET'])
def find():
	thing = jokes.find({})
	return parse_json(thing)

# does the heavy lifting of matchin setups to db
@app.route('/setup', methods=['POST'])
#@cross_origin()
async def dothething():
    sents = await getAllSetups()
    data = request.get_json(force=True)
    #print(data['setup'])
    output = await query({
	"inputs": {
		"source_sentence": data['setup'],
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
    outString = f'I am {int(mostSimilar * 100)}% sure you meant "{setup}" and I already know that joke... "{punchline}"'
    return jsonify(message = outString)



# Insert new joke
@app.route('/newjoke', methods=['POST'])
async def insertOne():
    data = request.get_json(force=True)
    queryObject = {
        'user': 'Tim',
        'setup': data['setup'],
		'punchline': data['punchline']
    }
    query = jokes.insert_one(queryObject)
    return jsonify(message="Joke Added to Database")

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