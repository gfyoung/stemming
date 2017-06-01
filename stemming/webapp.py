"""
Main web application for the user to provide documents for word counting.
"""

from flask import Flask, render_template, redirect, request, url_for
from .stemming import get_top_stems, stem_document

import uuid

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    doc_id = "@" + str(uuid.uuid4())
    document = request.form["document"]

    response = redirect(url_for("display", **{"id": doc_id}))
    response.set_cookie(doc_id, document)

    return response


@app.route("/display", methods=["GET"])
def display():
    doc_id = request.args.get("id")
    document = request.cookies.get(doc_id)

    if doc_id is None or document is None:
        return redirect(url_for("index"))

    top_stems = get_top_stems(stem_document(document))
    return render_template("result.html", stems=top_stems)
