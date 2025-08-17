from flask import Flask, request, Response
from jinja2 import Environment, select_autoescape
from jinja2.loaders import PackageLoader

from server.models import Card

jinja_env = Environment(loader=PackageLoader("server", "templates"), autoescape=select_autoescape)

app: Flask = Flask(__name__)


@app.get("/")
def index():
    return jinja_env.get_template("index.html").render()


# put register and refill options on this page
@app.get("/admin")
def admin():
    pass


@app.post("/pay/<card_id>/<bus_line>")
def pay(card_id, bus_line):
    try:
        card = Card.get_by_id(card_id)
    except Card.DoesNotExist:
        return Response(404)

    card.pay_ride(bus_line)


@app.post("/refill/<card_id>")
def refill(card_id):
    pass


@app.post("/register")
def register():
    card = Card.create(rides_left=5)
    return {"card_id": card.id, "checksum": card.checksum}
