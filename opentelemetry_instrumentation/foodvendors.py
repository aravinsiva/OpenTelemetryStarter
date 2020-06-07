import flask
from flask import request, make_response
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.ext.requests import RequestsInstrumentor
import time
import constants

# app cinfiguration
app = flask.Flask(__name__)
app.config["DEBUG"] = True

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


@app.route('/foodvendor', methods=['GET'])
def home():
    requests_counter = constants.create_requests_counter_metric()
    tracer = constants.make_tracer()
    with tracer.start_as_current_span("Searching for food availibility and prices"):
        food_query = request.headers.get("food")

        if food_query in constants.vend_food_prices:
            with tracer.start_as_current_span("Food item was found"):
                requests_counter.add(1, constants.staging_labels)
                time.sleep(5)
                return make_food_vendor_response(food_query)

        else:
            with tracer.start_as_current_span("Food item was not found"):
                resp = make_response("Food item not found")
                requests_counter.add(1, constants.staging_labels)
                time.sleep(5)
                return resp


def make_food_vendor_response(food_item):
    resp = make_response()
    resp.headers[food_item] = constants.vend_food_prices[food_item]
    return resp


if __name__ == '__main__':
    app.run(host="localhost", port=8001, debug=True)
