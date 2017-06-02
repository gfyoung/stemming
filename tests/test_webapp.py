"""
Tests for the web application views.
"""

from flask import abort
from tempfile import mkstemp
from stemming.webapp import app, init_db, get_db

import os


class WebAppTest(object):

    @classmethod
    def setup_class(cls):
        cls.db_fd, app.config["DATABASE"] = mkstemp()
        cls.client = app.test_client()
        app.config["TESTING"] = True

    def setup_method(self, _):
        with app.app_context():
            init_db()

    @classmethod
    def teardown_class(cls):
        os.close(cls.db_fd)
        os.unlink(app.config['DATABASE'])


class TestIndex(WebAppTest):

    @classmethod
    def setup_class(cls):
        super(TestIndex, cls).setup_class()

        cls.url = "/"

    @staticmethod
    def _check_data(data):
        """
        Check that the data returned contains the right information.

        Parameters
        ----------
        data : bytes
            The data to check.
        """

        assert b"submit" in data
        assert b"Stemming Web App" in data

    def test_get(self):
        rv = self.client.get(self.url)
        self._check_data(rv.data)

    def test_post(self):
        rv = self.client.post(self.url)
        self._check_data(rv.data)


class TestSubmit(WebAppTest):

    @classmethod
    def setup_class(cls):
        super(TestSubmit, cls).setup_class()

        cls.url = "/submit"
        cls.empty = dict(document="")
        cls.data = dict(document="The cat jumped")

    def test_get(self):
        rv = self.client.get(self.url, data=self.data)
        assert b"405 Method Not Allowed" in rv.data

    def test_post_bad_request(self):
        rv = self.client.post(self.url)
        assert b"400 Bad Request" in rv.data

    def test_post_redirect(self):
        rv = self.client.post(self.url, data=self.empty)
        assert b"Redirecting" in rv.data

        rv = self.client.post(self.url, data=self.data)
        assert b"Redirecting" in rv.data


class TestDisplay(WebAppTest):

    @classmethod
    def setup_class(cls):
        super(TestDisplay, cls).setup_class()

        cls.url = "/display"

        cls.id = "123456789"
        cls.empty_id = "987654321"

        cls.cmd = "INSERT INTO documents (doc_id, doc_text) values (?, ?)"

    def get(self, doc_id):
        """
        Helper method for performing the GET request.

        Parameters
        ----------
        doc_id : str
            The document ID to request.

        Returns
        -------
        get_response : flask.wrappers.Response
            A Flask response object containing the data from the response.
        """

        return self.client.get(self.url + "?id=" + doc_id)

    def test_get_redirect(self):
        rv = self.get("")
        assert b"Redirecting" in rv.data

        rv = self.get("non-existent")
        assert b"Redirecting" in rv.data

    def test_get_no_stems(self):
        with app.app_context():
            init_db()
            db = get_db()

            db.execute(self.cmd, [self.empty_id, ""])
            db.commit()

            rv = self.get(self.empty_id)
            assert b"No stems found" in rv.data

    def test_get_with_stems(self):
        with app.app_context():
            init_db()
            db = get_db()

            db.execute(self.cmd, [self.id, "The cat jumped"])
            db.commit()

            rv = self.get(self.id)

            assert b"the (1)" in rv.data
            assert b"cat (1)" in rv.data
            assert b"jump (1)" in rv.data

            assert b"Top Words" in rv.data
            assert b"Number in parentheses" in rv.data

    def test_post(self):
        rv = self.client.post(self.url, data={"id": "123456789"})
        assert b"405 Method Not Allowed" in rv.data


class TestErrorHandling(WebAppTest):

    def test_error_404(self):
        rv = self.client.get("/non-existent")

        assert b"Looks like you got a little lost" in rv.data
        assert b"want to submit a document, click" in rv.data

    def test_error_500(self):
        @app.route("/fails-miserably")
        def fail_immediately():
            abort(500)

        rv = self.client.get("/fails-miserably")

        assert b"Oh no! Something went wrong!" in rv.data
        assert b"Something went wrong on our end" in rv.data
