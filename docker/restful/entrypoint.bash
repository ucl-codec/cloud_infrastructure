#!/bin/bash

# UCL PASSIAN - launch script for Fed-BioMed restful container

# Remove the database
rm -rf /app/db.sqlite3

python manage.py migrate
python manage.py collectstatic --link --noinput
python manage.py createsuperuser --noinput
gunicorn -w 4 -b 0.0.0.0:8000 --log-level debug fedbiomed.wsgi&

wait $!
