import flask
from flask import request, make_response, render_template
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)
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

                resp = make_response()
                stores = "<h3>The food you are looking for is here </h3> \n"
                count = 1
                for i in constants.suppliers[food_query]:
                    resp.headers['Store' + str(count)] = i
                    stores += i + "\t"
                    count += 1
                requests_counter.add(1, constants.staging_labels)
                time.sleep(5)
                return resp


app.run()
