#!/bin/bash
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python import_questions.py
python import_careers.py
gunicorn --bind=0.0.0.0:${PORT:-8000} --timeout 600 personality_ai.wsgi:application
