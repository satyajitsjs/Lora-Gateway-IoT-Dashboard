#!/bin/bash

# Update system and install necessary packages
sudo apt update
sudo apt install -y ufw python3 python3-pip libssl-dev redis-server
sudo systemctl start redis-server


# Enable UFW and allow port 8000
sudo ufw allow 22
sudo ufw enable -y
sudo ufw status
sudo ufw allow 8000

# Install Python dependencies for the Django project
pip install -r requirement.txt


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

# for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do
#     sudo apt-get remove -y $pkg
# done

# sudo apt-get install -y ca-certificates curl
# sudo install -m 0755 -d /etc/apt/keyrings
# sudo curl -fsSL https://download.docker.com/linux/raspbian/gpg -o /etc/apt/keyrings/docker.asc
# sudo chmod a+r /etc/apt/keyrings/docker.asc

# echo \
#   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/raspbian \
#   $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
#   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# sudo apt-get update
# sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# # Verify Docker installation
# sudo docker run hello-world

# sudo docker build -t lora_server .
# sudo docker run -v /var/run/dbus:/var/run/dbus -v /etc/NetworkManager:/etc/NetworkManager -v /run/NetworkManager:/run/NetworkManager -p 80:80 --network host --name lora --privileged -t --restart always lora_server


sudo apt install docker.io
sudo systemctl start docker
sudo systemctl start docker
sudo systemctl enable docker
sudo docker --version
sudo docker build -t lora_server .
sudo docker run -v /var/run/dbus:/var/run/dbus -v /etc/NetworkManager:/etc/NetworkManager -v /run/NetworkManager:/run/NetworkManager -p 80:80 --network host --name lora --privileged -t --restart always lora_server