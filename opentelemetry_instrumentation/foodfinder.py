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

@app.route('/foodfinder', methods=['GET'])
def home():
        with tracer.start_as_current_span("Calling food supplier service for vendors"):

            food_query = request.headers.get("food")
            suppliers = requests.get('http://127.0.0.1:5000/foodsupplier',
            headers = {'food': food_query})
            
            requests_counter.add(1, staging_labels)
            time.sleep(5)


            return (str(suppliers.headers))




app.run(host="localhost", port = 8000, debug = True)