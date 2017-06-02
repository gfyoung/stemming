#!/bin/bash

git commit -a
git push heroku master

heroku run export FLASK_APP=stemming/webapp.py; flask initdb
heroku restart
