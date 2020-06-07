from opencensus.stats import aggregation
from opencensus.stats import measure
from opencensus.stats import view
from opencensus.stats import stats
from random import random
import logging

logger = logging.getLogger('Food Supplier')

# latency measurements
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

# Static list of food suppliers
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


def make_latency():
    for num in range(100):
        ms = random() * 5 * 1000

        mmap = stats.stats.stats_recorder.new_measurement_map()
        mmap.measure_float_put(LATENCY_MS, ms)
        mmap.record()

    logger.info("Fake latency recorded ({}: {})".format(num, ms))



