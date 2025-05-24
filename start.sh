#!/usr/bin/env bash

echo "Starting the Django application..."
cd src
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT 