#!/bin/bash
set -e

echo 'Trying to connect the database.'
while ! pg_isready -h db -p 5432 -U '$DB_USER'; do
  echo 'Waiting for PostgreSQL to be ready...'
  sleep 1
done
echo 'Database is ready.'

echo 'Trying to apply database migrations.'
if python /app/forum/manage.py showmigrations --plan | grep '\[ \]'; then
  echo 'Applying database migrations...'
  python /app/forum/manage.py migrate --fake-initial
else
  echo 'No migrations to apply.'
fi

echo 'Collecting static files...'
python /app/forum/manage.py collectstatic --noinput

echo 'Starting Gunicorn server...'
cd forum
gunicorn forum.wsgi:application --bind 0.0.0.0:8000 --workers "$GUNICORN_WORKERS" --timeout "$GUNICORN_TIMEOUT"