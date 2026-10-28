#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip to support modern binary wheels
pip install --upgrade pip setuptools wheel
pip install --prefer-binary -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python create_admin.py
