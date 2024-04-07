#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"
class AllRestaurants(Resource):
    def get(self):
        try:
            restaurants = [restaurant.to_dict(only=("address", "id", "name",)) for restaurant in Restaurant.query.all()]
            return restaurants, 200
        except Exception as e:
            return {"error": str(e)}, 404
class RestaurantById(Resource):
    def get(self, id):
        try:
            if restaurant := db.session.get(Restaurant, id):
                return restaurant.to_dict(), 200
            else:
                return {"error": "Restaurant not found"}, 404
        except Exception as e:
            return {"error": str(e)}, 400


class DeleteRestaurant(Resource):
    def delete(self, id):
        try:
            restaurant = db.session.get(Restaurant, id)
            if restaurant:
                db.session.delete(restaurant)
                db.session.commit()
                return {}, 204
            else:
                return {"error": "Restaurant not found"}, 404
        except Exception as e:
            return {"error": str(e)}, 400

class Pizzas(Resource):
    def get(self):
        try:
            pizzas = [pizza.to_dict(only=("id", "ingredients", "name")) for pizza in Pizza.query.all()]
            return pizzas, 200
        except Exception as e:
            return {"error": str(e)}, 400
class CreatePizza(Resource):
    def post(self):
        data = request.get_json()
        # breakpoint()
        try:
            restaurant_pizzas = RestaurantPizza(
                price=data["price"],
                pizza_id = data["pizza_id"],
                restaurant_id =data["restaurant_id"]
            )
            db.session.add(restaurant_pizzas)
            db.session.commit()
            return restaurant_pizzas.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400 # return { "errors": [str(e)]}, 400

api.add_resource(AllRestaurants, "/restaurants")
api.add_resource(RestaurantById, "/restaurants/<int:id>")
api.add_resource(DeleteRestaurant, "/restaurants/<int:id>")
api.add_resource(Pizzas, '/pizzas')
api.add_resource(CreatePizza, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
