#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Changing to src directory..."
cd src

echo "Checking environment variables..."
echo "DATABASE_URL: ${DATABASE_URL:0:30}..." # Показываем только первые 30 символов для безопасности
echo "DEBUG: $DEBUG"
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Build completed successfully!" 