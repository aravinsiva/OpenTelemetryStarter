import flask

import requests
from flask import request, make_response
from random import random
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.stats import aggregation
from opencensus.stats import measure
from opencensus.stats import stats
from opencensus.stats import view
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
import logging


vend_food_prices = {"eggs" : "$3.99",
                    "milk" : "$1.50",
                    "flour" : "$2.50",
                    "sugar" : "$2.00",
                    "salt"  :  "2.00"}



#app cinfiguration
app = flask.Flask(__name__)
app.config["DEBUG"] = True



#latency measurements
LATENCY_MS = measure.MeasureFloat(
    "task_latency",
    "The task latency in milliseconds",
    "ms")

LATENCY_VIEW = view.View(
    "task_latency_distribution",
    "The distribution of the task latencies",
    [],
    LATENCY_MS,
    # Latency in buckets: [>=0ms, >=100ms, >=200ms, >=400ms, >=1s, >=2s, >=4s]
    aggregation.DistributionAggregation(
        [100.0, 200.0, 400.0, 1000.0, 2000.0, 4000.0]))

#Setup tracing configurations
middleware = FlaskMiddleware(app)
logger = logging.getLogger('Food Supplier')

ze = ZipkinExporter(
        service_name="service-a",
        host_name="localhost",
        port=9411,
        endpoint="/api/v2/spans")
tracer = Tracer(exporter=ze)

@app.route('/foodvendor', methods=['GET'])
def home():

    food_query = request.headers.get("food")
    
    with tracer.span(name="Looking for food item in static db") as span:
        if food_query in vend_food_prices:
            with tracer.span(name = "Food item Found") as span:
                resp = make_response()
                resp.headers[food_query] = vend_food_prices[food_query]
                return resp

        else:
            with tracer.span(name = "Food item not Found") as span:
                resp = make_response("Food item not found")
                return resp
        

app.run(host="localhost", port = 8001, debug = True)