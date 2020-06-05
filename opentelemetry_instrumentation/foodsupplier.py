import flask
from flask import request, make_response, render_template
import logging
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



tracer = trace.get_tracer(__name__)
app = flask.Flask(__name__)
#app configuration
app.config["DEBUG"] = True

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

staging_labels = {"environment": "staging"}


#practice instrumenting multiple service application
#Static list of food suppliers
suppliers= {"eggs":["Hungry Man", "NoFrills", "Loblaws", "Food Basics"],
            "milk": ["Hungry Man", "NoFrills"],
            "flour":["Loblaws"],
            "sugar": ["Hungry Man", "NoFrills", "Loblaws"],
            "salt": ["NoFrills", "Loblaws"]}

metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__, True)
exporter = ConsoleMetricsExporter()
controller = PushController(meter, exporter, 5)


requests_counter = meter.create_metric(
    name="requests",
    description="number of requests",
    unit="1",
    value_type=int,
    metric_type=Counter,
    label_keys=("environment",),
)

@app.route('/foodsupplier', methods=['GET'])
def home():

    food_query = request.headers.get("food")
    with tracer.start_as_current_span("food being queiried:" + food_query):
        if (food_query not in suppliers):
            with tracer.start_as_current_span("food item:" + food_query + "Could not be found"):
                requests_counter.add(1, staging_labels)
                time.sleep(5)
                resp = make_response("Food item not found")
                return resp

        else:
            with tracer.start_as_current_span("food item found!"):

                resp = make_response()
                stores = "<h3>The food you are looking for is here </h3> \n" 
                count = 1
                for i in suppliers[food_query]:
                    resp.headers['Store' + str(count)] = i
                    stores += i + "\t"
                    count += 1
                requests_counter.add(1, staging_labels)
                time.sleep(5)
                return resp


app.run()