#!/bin/bash

git restore .
git clean -df 

# Function to run Django management commands
run_django_commands() {
    python3 manage.py makemigrations
    python3 manage.py migrate

    read -p "Enter the gateway ID: " gateway_id

    python3 manage.py create_gateway "$gateway_id"

    # Create superuser with predefined data
    python3 manage.py shell <<EOF
from django.contrib.auth.models import User

# Check if the superuser already exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
EOF

    # python3 manage.py runserver 0.0.0.0:8000
}

# Run Django management commands
run_django_commands

sudo docker build -t lora_server .
sudo docker container restart lora