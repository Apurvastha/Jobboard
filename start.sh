#!/bin/bash
celery -A jobboard worker --loglevel=info --concurrency=2 &
CELERY_PID=$!
gunicorn jobboard.wsgi:application --bind 0.0.0.0:$PORT --workers 2
kill $CELERY_PID