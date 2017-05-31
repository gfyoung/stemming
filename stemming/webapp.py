"""
Main web application for the user to provide documents for word counting.
"""

from flask import Flask, render_template, request
from .stemming import get_top_stems, stem_document

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    document = request.form["document"]
    top_stems = get_top_stems(stem_document(document))
    return render_template("result.html", stems=top_stems)
