
from flask import Flask

app = Flask(__name__)

from app.routes import pages
app.register_blueprint(pages)