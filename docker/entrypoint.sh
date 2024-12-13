#!/bin/bash

echo "Waiting for database..."
while ! python -c "import socket; s = socket.socket(); s.connect(('db', 5432))"; do
  sleep 1
done
echo "Database is ready."

python forum/manage.py makemigrations
python forum/manage.py migrate --fake-initial
python forum/manage.py collectstatic --noinput

gunicorn forum.forum.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120