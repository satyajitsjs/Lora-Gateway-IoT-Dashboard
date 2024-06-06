# Remake 
```bash
chmod +x remake.sh
./remake.sh
```

# INstall THe git and clone the repo
```bash
sudo apt install -y git
git clone https://satyajit2024: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@github.com/satyajit2024/lora_dev_v2.git/
```

# Build the docker with make
```bash
cd lora_dev_v2
chmod +x make.sh
./make.sh
```

## For see the docker logs 
```bash
sudo docker container logs lora
```

## For go inside the docker container 
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

# Cronab 
```bash
crontab -e
```

# Add in crontab 
```bash
0 * * * * /usr/bin/sudo truncate -s 0 /var/lib/docker/containers/{container_id}/{container_id}-js>
0 * * * * /usr/bin/sudo docker container restart node
@reboot /usr/bin/python3 /home/pi/lora_dev_v2/load_control.py >> /home/pi/load_cotrol.log 2>&1
```

## Start The Docker for ngrok For bash
```bash
sudo docker run --name my-ngrok-container --net=host --restart always -it -e NGROK_AUTHTOKEN=2eoHdhyjTENMnvyD9xP5NNFkXgM_41NvmR4i8Vor1hZgUtDoV ngrok/ngrok:latest tcp 22
```

## model configuration
```bash
sudo apt install network-manager modemmanager
sudo apt install libqmi-utils udhcpc
sudo systemctl start NetworkManager
sudo systemctl enable NetworkManager
nmcli c add type gsm ifname '*' con-name airtel apn airtelgprs.com connection.autoconnect yes
```


## GSM MODEM CONFIG
```bash
sudo apt install network-manager modemmanager
sudo apt install libqmi-utils udhcpc
lsusb
sudo systemctl start NetworkManager
sudo systemctl enable NetworkManager
sudo systemctl start ModemManager
sudo systemctl enable ModemManager
```