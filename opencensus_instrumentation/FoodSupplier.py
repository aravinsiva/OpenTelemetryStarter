import flask
from flask import request, make_response, render_template
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.tracer import Tracer
from opencensus.stats import stats
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
import logging
import constants

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Setup tracing configurations
middleware = FlaskMiddleware(app)
logger = logging.getLogger('Food Supplier')


@app.route('/foodsupplier', methods=['GET'])
def home():
    tracer = Tracer(exporter=create_zipkin_exporter())
    food_query = request.headers.get("food")
    stats.stats.view_manager.register_view(constants.LATENCY_VIEW)

    with tracer.span(name="Looking for food item in static db"):
        if food_query not in constants.suppliers:
            logger.error('Food item could not be found')
            with tracer.span(name="No food item Found"):
                constants.make_latency()
                return make_response("Food Item not found")

        else:
            with tracer.span(name="Food item Found"):
                logger.info('Food Item Succesfully found')
                resp = make_food_supplier_response(food_query)
                constants.make_latency()
                return resp


def make_food_supplier_response(food_item):
    resp = make_response()
    header_number = 1

    for supplier in constants.suppliers[food_item]:
        resp.headers['Store' + str(header_number)] = supplier
        header_number += 1
    return resp


def create_zipkin_exporter():
    ze = ZipkinExporter(
        service_name="Food Supplier Service",
        host_name="localhost",
        port=9411,
        endpoint="/foodsuppliers/spans")

    return ze


app.run()
