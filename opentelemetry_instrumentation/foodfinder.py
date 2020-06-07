import flask
import requests
from flask import request, make_response
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.ext.requests import RequestsInstrumentor

app = flask.Flask(__name__)

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


@app.route('/foodfinder', methods=['GET'])
def home():
    # with tracer.start_as_current_span("Calling food supplier service for vendors"):

    food_query = request.headers.get("food")
    suppliers = requests.get('http://127.0.0.1:5000/foodsupplier',
                             headers={'food': food_query})

    price = requests.get('http://localhost:8001/foodvendor',
                         headers={'food': food_query})

    return str(suppliers.headers) + '\n' + str(price.headers)


app.run(host="localhost", port=8000, debug=True)
