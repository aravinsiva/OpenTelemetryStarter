import flask

import requests
from flask import request, make_response
from random import random
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.ext.requests import RequestsInstrumentor 

import time

from opentelemetry import metrics
from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricsExporter
from opentelemetry.sdk.metrics.export.controller import PushController

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)

RequestsInstrumentor().instrument()
tracer = trace.get_tracer(__name__)
staging_labels = {"environment": "staging"}

metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__, True)
exporter = ConsoleMetricsExporter()
controller = PushController(meter, exporter, 5)

vend_food_prices = {"eggs" : "$3.99",
                    "milk" : "$1.50",
                    "flour" : "$2.50",
                    "sugar" : "$2.00",
                    "salt"  :  "2.00"}


requests_counter = meter.create_metric(
    name="requests",
    description="number of requests",
    unit="1",
    value_type=int,
    metric_type=Counter,
    label_keys=("environment",),
)

#app cinfiguration
app = flask.Flask(__name__)
app.config["DEBUG"] = True

FlaskInstrumentor().instrument_app(app)

@app.route('/foodvendor', methods=['GET'])
def home():
        with tracer.start_as_current_span("Searching for food availibility and prices"):

            food_query = request.headers.get("food")
            
            if food_query in vend_food_prices:
                with tracer.start_as_current_span("Food item was found"):

                    resp = make_response()
                    resp.headers[food_query] = vend_food_prices[food_query]
                    requests_counter.add(1, staging_labels)
                    time.sleep(5)
                    return resp

            else:
                with tracer.start_as_current_span("Food item was not found"):

                    requests_counter.add(1, staging_labels)
                    time.sleep(5)
                    resp = make_response("Food item not found")
                    requests_counter.add(1, staging_labels)
                    time.sleep(5)
                    return resp
        

app.run(host="localhost", port = 8001, debug = True)