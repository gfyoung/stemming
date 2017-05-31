"""
Tests for the web application views.
"""

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
        assert b"No stems found!" in rv.data

        rv = self.client.post(self.url, data=self.data)

        assert b"<li>cat</li>" in rv.data
        assert b"<li>the</li>" in rv.data
        assert b"<li>jump</li>" in rv.data
