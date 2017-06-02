"""
Main web application for the user to provide documents for word counting.
"""

from flask import (Flask, Markup, g, render_template,
                   redirect, request, url_for)
from .stemming import get_top_stems, stem_document

import os
import uuid
import sqlite3

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, "stemming.db")
))


def connect_db():
    """
    Connect to the database and return the connection.

    Returns
    -------
    db_conn : sqlite3.Connection
        A sqlite3 connection to the database.
    """

    rv = sqlite3.connect(app.config["DATABASE"])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """
    Get the database connection and store in the global state.

    Returns
    -------
    db_conn : sqlite3.Connection
        A sqlite3 connection to the database.
    """

    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()

    return g.sqlite_db


@app.teardown_appcontext
def close_db(_):
    """
    Close the connection to the database.
    """

    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


def init_db():
    """
    Initialize all tables in the database as defined in `schema.sql`.
    """

    db = get_db()

    with app.open_resource("schema.sql", mode="r") as f:
        db.cursor().executescript(f.read())

    db.commit()


@app.cli.command("initdb")
def initdb_command():
    """
    Flask command for initializing the database.
    """

    init_db()
    print("Initialized database")


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    doc_id = str(uuid.uuid4())
    document = request.form["document"]

    db = get_db()
    cmd = "INSERT INTO documents (doc_id, doc_text) values (?, ?)"

    db.execute(cmd, [doc_id, document])
    db.commit()

    response = redirect(url_for("display", **{"id": doc_id}))
    return response


@app.route("/display", methods=["GET"])
def display():
    db = get_db()

    document = None
    doc_id = request.args.get("id")

    if doc_id is not None:
        cmd = "SELECT doc_text FROM documents WHERE doc_id=?"
        cur = db.execute(cmd, [doc_id])

        document = cur.fetchone()
        if document is not None:
            document = document["doc_text"]

    if doc_id is None or document is None:
        return redirect(url_for("index"))

    matches = stem_document(document)
    top_stems = get_top_stems(matches)

    cmd = "INSERT INTO matches (doc_id, stem, matches) values (?, ?, ?)"

    for stem, stem_matches in matches.items():
        matches = ",".join(stem_matches)

        db.execute(cmd, [doc_id, stem, matches])
        db.commit()

    return render_template("result.html", stems=top_stems)


@app.route("/match", methods=["GET"])
def match():
    db = get_db()

    document = None
    stem = request.args.get("stem")
    doc_id = request.args.get("id")

    if not (stem is None or doc_id is None):
        cmd = "SELECT doc_text FROM documents WHERE doc_id=?"
        cur = db.execute(cmd, [doc_id])

        document = cur.fetchone()
        if document is not None:
            document = document["doc_text"]

    if stem is None or doc_id is None or document is None:
        return redirect(url_for("index"))

    cmd = "SELECT matches FROM matches WHERE doc_id=? AND stem=?"
    cur = db.execute(cmd, [doc_id, stem])

    matches = cur.fetchone()

    if matches is None:
        return redirect(url_for("index"))

    matches = matches["matches"]
    matches = set(matches.split(","))

    for stem_match in matches:
        document = document.replace(stem_match, ("<span class='match'>"
                                                 + stem_match + "</span>"))

    return render_template("match.html", document=Markup(document), stem=stem)


@app.route("/you-done-goofed", methods=["GET", "POST"])
def error_user():
    return render_template("404.html")


@app.errorhandler(400)
def error_400(_):
    return redirect(url_for("error_user"))


@app.errorhandler(404)
def error_404(_):
    return redirect(url_for("error_user"))


@app.errorhandler(405)
def error_405(_):
    return redirect(url_for("error_user"))


@app.errorhandler(500)
def error_500(_):
    return render_template("500.html")
