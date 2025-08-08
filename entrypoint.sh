#!/bin/bash
set -e

echo "Waiting for postgres..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

python manage.py migrate
python manage.py collectstatic --noinput

# Load initial data if it exists
python manage.py setup_initial_data || true

exec "$@"