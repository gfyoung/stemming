"""
Tests for the web application views.
"""

from flask import abort  # noqa
from tempfile import mkstemp
from stemming.webapp import app, init_db, get_db

import os
import pytest


class WebAppTest(object):

    @classmethod
    def setup_class(cls):
        cls.db_fd, app.config["DATABASE"] = mkstemp()
        cls.client = app.test_client()
        app.config["TESTING"] = True

    def setup_method(self, _):
        # For tests that just query data, this setup is sufficient.
        # However, for tests that write to the database, it is necessary
        # to run the entire test under the app_context, including creating,
        # writing, and querying, as the database state expires once you
        # leave the app_context.
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
        # 405 error --> redirect to error page
        rv = self.client.get(self.url, data=self.data)
        assert b"Redirecting" in rv.data

    def test_post_bad_request(self):
        # 400 error --> redirect to error page
        rv = self.client.post(self.url)
        assert b"Redirecting" in rv.data

    def test_post_redirect(self):
        # Successful request --> redirect to display page
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
        # 405 error --> redirect to error page
        rv = self.client.post(self.url, data={"id": "123456789"})
        assert b"Redirecting" in rv.data


class TestMatch(WebAppTest):

    @classmethod
    def setup_class(cls):
        super(TestMatch, cls).setup_class()

        cls.url = "/match"
        cls.doc_add = "INSERT INTO documents (doc_id, doc_text) values (?, ?)"
        cls.stem_add = ("INSERT INTO matches (doc_id, stem, "
                        "matches) values (?, ?, ?)")

    def get(self, doc_id, stem):
        """
        Helper method for performing the GET request.

        Parameters
        ----------
        doc_id : str
            The document ID to request.
        stem : str
            The stem for which to find matches.

        Returns
        -------
        get_response : flask.wrappers.Response
            A Flask response object containing the data from the response.
        """

        return self.client.get(self.url + "?id=" + doc_id + "&stem=" + stem)

    def test_get_redirect(self):
        rv = self.get("", "")
        assert b"Redirecting" in rv.data

        rv = self.get("", "non-existent")
        assert b"Redirecting" in rv.data

        rv = self.get("non-existent", "")
        assert b"Redirecting" in rv.data

        rv = self.get("non-existent", "non-existent")
        assert b"Redirecting" in rv.data

        # Document exists, but stem does not.
        with app.app_context():
            init_db()
            db = get_db()

            doc_id = "123456789"

            db.execute(self.doc_add, [doc_id, "text"])
            db.commit()

            rv = self.get(doc_id, "non-existent")
            assert b"Redirecting" in rv.data

    def test_get_with_stem(self):
        with app.app_context():
            init_db()
            db = get_db()

            doc_id = "123456789"
            doc_text = "The cat jumped the fence."

            db.execute(self.doc_add, [doc_id, doc_text])

            stem, stem_matches = "the", "The,the"

            db.execute(self.stem_add, [doc_id, stem, stem_matches])
            db.commit()

            stem, stem_matches = "jump", "jumped"

            db.execute(self.stem_add, [doc_id, stem, stem_matches])
            db.commit()

            rv = self.get(doc_id, "the")
            assert b"The</span>" in rv.data
            assert b"the</span>" in rv.data
            assert b"jumped</span>" not in rv.data

            rv = self.get(doc_id, "jump")
            assert b"The</span>" not in rv.data
            assert b"the</span>" not in rv.data
            assert b"jumped</span>" in rv.data

    def test_post(self):
        # 405 error --> redirect to error page
        rv = self.client.post(self.url, data={"id": "123456789",
                                              "stem": "stem"})
        assert b"Redirecting" in rv.data


class TestClientErrorHandling(WebAppTest):

    @pytest.mark.parametrize("method", ["get", "post"])
    def test_error_client(self, method):
        rv = getattr(self.client, method)("/you-done-goofed")

        assert b"Looks like you got a little lost" in rv.data
        assert b"want to submit a document, click" in rv.data

    @pytest.mark.parametrize("error", [400, 404, 405])
    def test_error_client_redirect(self, error):
        route = "/client-failure-{error}".format(error=error)

        # Need to define methods and endpoints based on error code.
        exec("""
@app.route(route)
def client_fail_{error}():
    abort({error})""".format(error=error))

        rv = self.client.get(route)
        assert b"Redirecting" in rv.data


class TestServerErrorHandling(WebAppTest):

    @pytest.mark.parametrize("method", ["get", "post"])
    def test_error_server(self, method):
        rv = getattr(self.client, method)("/we-done-goofed")

        assert b"Oh no! Something went wrong!" in rv.data
        assert b"Something went wrong on our end" in rv.data

    @pytest.mark.parametrize("error", [500, 501])
    def test_error_server_redirect(self, error):
        route = "/server-failure-{error}".format(error=error)

        # Need to define methods and endpoints based on error code.
        exec("""
@app.route(route)
def server_fail_{error}():
    abort({error})""".format(error=error))

        rv = self.client.get(route)
        assert b"Redirecting" in rv.data
