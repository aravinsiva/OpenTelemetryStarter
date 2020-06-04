import flask
from flask import request, make_response, render_template
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.stats import aggregation
from opencensus.stats import measure
from opencensus.stats import stats
from opencensus.stats import view
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
import logging
from random import random

app = flask.Flask(__name__)
#app configuration
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

@app.route('/foodsupplier', methods=['GET'])
def home():
    food_query = request.headers.get("food")
    stats.stats.view_manager.register_view(LATENCY_VIEW)

    with tracer.span(name="Looking for food item in static db") as span:
        if food_query not in suppliers:
            logger.error('Food item could not be found')
            with tracer.span(name = "No food item Found"):
                return make_response(404)

        else:
            with tracer.span(name = "Food item Found") as span:
                resp = make_response()
                logger.info('Food Item Succesfully found')
                stores = "<h3>The food you are looking for is here </h3> \n" 
                count = 1
                for i in suppliers[food_query]:
                    resp.headers['Store' + str(count)] = i
                    stores += i + "\t"
                    count += 1
                for num in range(100):
                    ms = random() * 5 * 1000

                    mmap = stats.stats.stats_recorder.new_measurement_map()
                    mmap.measure_float_put(LATENCY_MS, ms)
                    mmap.record()

                print("Fake latency recorded ({}: {})".format(num, ms))
                return resp


app.run()