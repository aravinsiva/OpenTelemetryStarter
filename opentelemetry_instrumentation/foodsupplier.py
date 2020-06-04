import flask
from flask import request, make_response, render_template
import logging
from random import random
from opentelemetry.ext.flask import FlaskInstrumentor


app = flask.Flask(__name__)
#app configuration
app.config["DEBUG"] = True

FlaskInstrumentor().instrument_app(app)
#practice instrumenting multiple service application
#Static list of food suppliers
suppliers= {"eggs":["Hungry Man", "NoFrills", "Loblaws", "Food Basics"],
            "milk": ["Hungry Man", "NoFrills"],
            "flour":["Loblaws"],
            "sugar": ["Hungry Man", "NoFrills", "Loblaws"],
            "salt": ["NoFrills", "Loblaws"]}


@app.route('/foodsupplier', methods=['GET'])
def home():
    food_query = request.headers.get("food")

    if food_query not in suppliers:
        return make_response(404)

    else:
        resp = make_response()
        stores = "<h3>The food you are looking for is here </h3> \n" 
        count = 1
        for i in suppliers[food_query]:
            resp.headers['Store' + str(count)] = i
            stores += i + "\t"
            count += 1
        
        return resp


app.run()