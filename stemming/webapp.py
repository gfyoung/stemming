"""
Main web application for the user to provide documents for word counting.
"""

from flask import (Flask, Markup, make_response, render_template,
                   redirect, request, url_for)
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

    matches = stem_document(document)
    top_stems = get_top_stems(matches)

    response = make_response(render_template("result.html", stems=top_stems))

    for stem, stem_matches in matches.items():
        response.set_cookie(doc_id + "@@" + stem, ",".join(stem_matches))

    return response


@app.route("/match", methods=["GET"])
def match():
    stem = request.args.get("stem")
    doc_id = request.args.get("id")
    document = request.cookies.get(doc_id)

    if stem is None or doc_id is None or document is None:
        return redirect(url_for("index"))

    matches = request.cookies.get(doc_id + "@@" + stem)
    matches = set(matches.split(","))

    for stem_match in matches:
        document = document.replace(stem_match, ("<span class='match'>"
                                                 + stem_match + "</span>"))

    return render_template("match.html", document=Markup(document), stem=stem)
