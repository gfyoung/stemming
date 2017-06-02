#!/bin/bash

addAll='false'
initDB='false'

while getopts 'Aih' flag; do
    case "${flag}" in
        h) echo 'deploy.sh - Helper for Heroku deployment'
           echo ''
           echo 'Usage: deploy.sh [options]'
           echo ''
           echo 'options:'
           echo '-h: show brief help'
           echo '-A: add all staged changes'
           echo '-i: initialize database and restart'
           exit 0
           ;;
        A) addAll='true' ;;
        i) initDB='true' ;;
     esac
done

if [ ${addAll} = 'true' ]; then
    git add -A
fi

git commit -a
git push -f heroku master

if [ ${initDB} = 'true' ]; then
    heroku run export FLASK_APP=stemming/webapp.py; flask initdb
    heroku restart
fi
