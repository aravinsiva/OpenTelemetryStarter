import flask
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)
from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.ext.requests import RequestsInstrumentor
from opentelemetry import metrics

from opentelemetry.sdk.metrics.export import ConsoleMetricsExporter
from opentelemetry.sdk.metrics.export.controller import PushController

staging_labels = {"environment": "staging"}

suppliers = {"eggs": ["Hungry Man", "NoFrills", "Loblaws", "Food Basics"],
             "milk": ["Hungry Man", "NoFrills"],
             "flour": ["Loblaws"],
             "sugar": ["Hungry Man", "NoFrills", "Loblaws"],
             "salt": ["NoFrills", "Loblaws"]}

vend_food_prices = {"eggs" : "$3.99",
                    "milk" : "$1.50",
                    "flour" : "$2.50",
                    "sugar" : "$2.00",
                    "salt"  :  "2.00"}


def create_requests_counter_metric():
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

    return requests_counter


def make_tracer():
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        SimpleExportSpanProcessor(ConsoleSpanExporter())
    )

    tracer = trace.get_tracer(__name__)

    return tracer
