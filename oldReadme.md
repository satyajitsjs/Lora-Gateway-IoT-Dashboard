# Start:
```bash
sudo apt update
sudo apt install ufw
sudo ufw enable
sudo ufw status
sudo ufw allow 8000

sudo apt install python3
sudo apt install python3-pip
sudo apt install libssl-dev

sudo apt install git

sudo apt install redis-server
sudo service redis-server start
```

### Set The Srver:
```bash
pip install -r requirement.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
```


## SuperUSER Create
![SuperUser Create](https://lora-bit.s3.amazonaws.com/lora-redme/image.png)
1. **Username**: admin
2. **Email Address**: admin@gmail.com
3. **Password**: admin
4. **Password (again)**: admin
- The password is too similar to the username.
- This password is too short. It must contain at least 8 characters.
- This password is too common.
- Bypass password validation and create user anyway? [y/N]: y
- Superuser created successfully.


### Create the Gateway:
```bash
python3 manage.py create_gateway
```

### Run The Server:
```bash
python3 manage.py runserver 0.0.0.0:8000
```


### Install Docker:
```bash
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/raspbian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Set up Docker's APT repository:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/raspbian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# To install the latest version, run:
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify that the installation is successful by running the hello-world image:
sudo docker run hello-world
```


### DockerFile build and run:
```bash
sudo docker build -t lora_server .
sudo docker run -v /var/run/dbus:/var/run/dbus -v /etc/NetworkManager:/etc/NetworkManager -v /run/NetworkManager:/run/NetworkManager -p 80:80 --network host --name lora --privileged -t --restart always lora_server
```

## See logs:
```bash
sudo docker container logs lora
```

## Inside the container:
```bash
sudo docker container exec -it lora bash
```


## If rpi 64 bit:
```bash
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl start docker
sudo systemctl enable docker
sudo docker --version
sudo docker build -t lora_server .
sudo docker run -v /var/run/dbus:/var/run/dbus -v /etc/NetworkManager:/etc/NetworkManager -v /run/NetworkManager:/run/NetworkManager -p 80:80 --network host --name lora --privileged -t --restart always lora_server
```