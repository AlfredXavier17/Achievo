#!/usr/bin/env bash
set -o errexit  # Exit script if any command fails

pip install -r requirements.txt          # Install Python dependencies
python manage.py collectstatic --noinput # Gather static files (CSS/JS)
python manage.py migrate                 # Apply database migrations