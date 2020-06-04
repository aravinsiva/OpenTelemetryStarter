import flask
from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.stats import aggregation
from opencensus.stats import measure
from opencensus.stats import stats
from opencensus.stats import view
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
import logging
from random import random
import requests
from flask import request, make_response

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

#practice instrumenting multiple service application
#Static list of food suppliers
suppliers= {"eggs":["Hungry Man", "NoFrills", "Loblaws", "Food Basics"],
            "milk": ["Hungry Man", "NoFrills"],
            "flour":["Loblaws"],
            "sugar": ["Hungry Man", "NoFrills", "Loblaws"],
            "salt": ["NoFrills", "Loblaws"]}

#Setup tracing configurations
middleware = FlaskMiddleware(app)
logger = logging.getLogger('Food Supplier')

#Initialize zipkin exporter
ze = ZipkinExporter(
        service_name="service-a",
        host_name="localhost",
        port=9411,
        endpoint="/api/v2/spans")
tracer = Tracer(exporter=ze)


@app.route('/foodfinder', methods=['GET'])
def home():
    with tracer.span(name="Calling Food Supplier Service") as span:
        logger.info("Callingggg food supplier service")
        food_query = request.headers.get("food")
        suppliers = requests.get('http://127.0.0.1:5000/foodsupplier',
        headers = {'food': food_query})
    


    return (str(suppliers.headers))




app.run(host="localhost", port = 8000, debug = True)