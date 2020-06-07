import flask
from flask import request, make_response, render_template
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.ext.requests import RequestsInstrumentor
import time
import constants

app = flask.Flask(__name__)

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


@app.route('/foodsupplier', methods=['GET'])
def home():
    food_query = request.headers.get("food")
    requests_counter = constants.create_requests_counter_metric()
    tracer = constants.make_tracer()
    with tracer.start_as_current_span("food being queiried:" + food_query):
        if food_query not in constants.suppliers:
            with tracer.start_as_current_span("food item:" + food_query + "Could not be found"):
                requests_counter.add(1, constants.staging_labels)
                time.sleep(5)
                resp = make_response("Food item not found")
                return resp

        else:
            with tracer.start_as_current_span("food item found!"):
                requests_counter.add(1, constants.staging_labels)
                time.sleep(5)
                return make_food_supplier_response(food_query)

def make_food_supplier_response(food_item):
    resp = make_response()
    count = 1
    for i in constants.suppliers[food_item]:
        resp.headers['Store' + str(count)] = i
        count += 1
    return resp


app.run()
