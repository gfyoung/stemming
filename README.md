[![Build Status](https://travis-ci.org/gfyoung/stemming.svg?branch=master)](https://travis-ci.org/gfyoung/stemming)

# stemming

Web application for counting words in a document.

# Framework

This web application is built on top of `Flask`, a nice light-weight web framework
in Python that you can use if you don't need all of the out-of-the-box functionality
that something like `Django` provides. Other than that, the website is pretty simple.
There are no special JS frameworks nor special CSS libraries. Everything is written
largely from scratch.

# Usage

If you want to run the website locally, it is necessary to setup the database,
which you can do as follows:

~~~
export FLASK_APP=stemming/webapp.py
pip install flask -U
flask initdb
~~~

After executing those commands, run this command below, and the website will
run on `localhost:5000`:

~~~
flask run
~~~

If you want to run the website using the `Procfile`, in addition to the database
initialization above, execute the commands below, and it will run on `localhost:8000`:

~~~
pip install gunicorn -U
gunicorn stemming:app
~~~

To run tests, execute the following commands:

~~~
pip install flask pytest -U
pytest
~~~

Note that all three instructions are assuming that you are at the top
directory of the pulled-down Git repository. These instructions are also meant
to be standalone (i.e. they will work out-of-the-box individually).
