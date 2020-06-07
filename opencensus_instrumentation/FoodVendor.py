import flask
from flask import request, make_response
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.tracer import Tracer
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
import logging
import constants

# app cinfiguration
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Setup tracing configurations
middleware = FlaskMiddleware(app)
logger = logging.getLogger('Food Supplier')


@app.route('/foodvendor', methods=['GET'])
def home():
    food_query = request.headers.get("food")
    tracer = Tracer(exporter=create_zipkin_exporter())
    with tracer.span(name="Looking for food item in static db"):
        if food_query in constants.vend_food_prices:
            with tracer.span(name="Food item Found"):
                constants.make_latency()
                return get_food_vendor_response(food_query)

        else:
            with tracer.span(name="Food item not Found"):
                resp = make_response("Food item not found")
                constants.make_latency()
                return resp


def get_food_vendor_response(food_item):
    resp = make_response()
    resp.headers[food_item] = constants.vend_food_prices[food_item]
    return resp


def create_zipkin_exporter():
    ze = ZipkinExporter(
        service_name="Food Vendor Service",
        host_name="localhost",
        port=9411,
        endpoint="/foodvendor/spans")
    return ze


app.run(host="localhost", port=8001, debug=True)
