from flask import Flask, request, Response
from jinja2 import Environment, select_autoescape
from jinja2.loaders import PackageLoader

jinja_env = Environment(loader=PackageLoader("server", "templates"), autoescape=select_autoescape)

app: Flask = Flask(__name__)


@app.get("/")
def index():
    return jinja_env.get_template("index.html").render()


# put register and refill options on this page
@app.get("/admin")
def admin():
    pass


@app.post("/validate/<card_id>")
def validate(card_id):
    pass


@app.post("/refill/<card_id>")
def refill(card_id):
    pass


@app.post("/register")
def register():
    pass
