"""
Tests for the web application views.
"""

from flask import abort
from stemming.webapp import app


class TestIndex(object):

    def setup_class(self):
        self.url = "/"
        self.client = app.test_client()

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


class TestSubmit(object):

    def setup_class(self):
        self.url = "/submit"
        self.client = app.test_client()

        self.empty = dict(document="")
        self.data = dict(document="The cat jumped")

    def test_get(self):
        rv = self.client.get(self.url, data=self.data)
        assert b"405 Method Not Allowed" in rv.data

    def test_post(self):
        rv = self.client.post(self.url)
        assert b"400 Bad Request" in rv.data

        rv = self.client.post(self.url, data=self.empty)
        assert b"Redirecting" in rv.data

        rv = self.client.post(self.url, data=self.data)
        assert b"Redirecting" in rv.data


class TestDisplay(object):

    def setup_class(self):
        self.url = "/display"
        self.client = app.test_client()
        self.server_name = "test_server"

        self.id = "123456789"
        self.client.set_cookie(server_name=self.server_name, key=self.id,
                               value="The cat jumped")

        self.empty_id = "987654321"
        self.client.set_cookie(server_name=self.server_name,
                               key=self.empty_id, value="")

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

    def test_get(self):
        rv = self.get("")
        assert b"Redirecting" in rv.data

        rv = self.get("non-existent")
        assert b"Redirecting" in rv.data

        rv = self.get(self.empty_id)
        assert b"No stems found" in rv.data

        rv = self.get(self.id)

        assert b"the (1)" in rv.data
        assert b"cat (1)" in rv.data
        assert b"jump (1)" in rv.data

        assert b"Top Words" in rv.data
        assert b"Number in parentheses" in rv.data

    def test_post(self):
        rv = self.client.post(self.url, data=self.id)
        assert b"405 Method Not Allowed" in rv.data


class TestErrorHandling(object):

    def setup_class(self):
        self.client = app.test_client()

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
