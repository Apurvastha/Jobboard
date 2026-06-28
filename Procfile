web: sh -c 'gunicorn jobboard.wsgi:application --bind 0.0.0.0:$PORT --workers 2'
worker: celery -A jobboard worker --loglevel=info