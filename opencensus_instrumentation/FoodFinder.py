import flask
from opencensus.trace.tracer import Tracer
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
import logging
import requests
from flask import request, make_response
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
import constants

# app cinfiguration
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Setup tracing configurations
middleware = FlaskMiddleware(app)
logger = logging.getLogger('Food Supplier')


@app.route('/foodfinder', methods=['GET'])
def home():
    tracer = Tracer(exporter=create_zipkin_exporter())
    with tracer.span(name="Calling Food Supplier Service"):
        logger.info("Callingggg food supplier service")
        constants.make_latency()
        food_query = request.headers.get("food")
        suppliers = requests.get('http://127.0.0.1:5000/foodsupplier',
                                 headers={'food': food_query})
        price = requests.get('http://localhost:8001/foodvendor',
                             headers={'food': food_query})

    return str(suppliers.headers) + '\n' + str(price.headers)


def create_zipkin_exporter():
    ze = ZipkinExporter(
        service_name="service-a",
        host_name="localhost",
        port=9411,
        endpoint="/foodfinder/spans")
    return ze


app.run(host="localhost", port=8000, debug=True)
