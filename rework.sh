#!/usr/bin/env bash

rm db.sqlite3
rm */migrations/00*.py

python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser
