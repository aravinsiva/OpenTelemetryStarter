import flask

import requests
from opentelemetry.ext.flask import FlaskInstrumentor
from flask import request, make_response

#app cinfiguration
app = flask.Flask(__name__)
app.config["DEBUG"] = True

FlaskInstrumentor().instrument_app(app)

@app.route('/foodfinder', methods=['GET'])
def home():

    food_query = request.headers.get("food")
    suppliers = requests.get('http://127.0.0.1:5000/foodsupplier',
    headers = {'food': food_query})



    return (str(suppliers.headers))




app.run(host="localhost", port = 8000, debug = True)