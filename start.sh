#!/bin/bash
celery -A jobboard worker --loglevel=info &
CELERY_PID=$!
gunicorn jobboard.wsgi:application --bind 0.0.0.0:$PORT --workers 2
kill $CELERY_PID