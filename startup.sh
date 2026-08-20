#!/bin/bash
python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn --bind=0.0.0.0:${PORT:-8000} --timeout 600 personality_ai.wsgi:application
