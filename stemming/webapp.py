"""
Main web application for the user to provide documents for word counting.
"""

from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Coming soon!"
