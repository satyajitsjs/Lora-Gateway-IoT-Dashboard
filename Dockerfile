# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory for the application
WORKDIR /app

# Copy the requirements file into the container
COPY requirement.txt requirement.txt

# Install system dependencies
RUN apt-get update && \
    apt-get install -y python3-gpiozero network-manager spi-tools tzdata cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install project dependencies
RUN ln -fs /usr/share/zoneinfo/Asia/Kolkata /etc/localtime
RUN pip install --no-cache-dir -r requirement.txt
RUN pip install spidev gpiozero RPi.GPIO  # Add RPi.GPIO here

# Download and install kernel headers manually
RUN apt-get update && \
    apt-get install -y wget && \
    wget https://github.com/raspberrypi/linux/archive/rpi-5.10.y.tar.gz && \
    tar xzf rpi-5.10.y.tar.gz && \
    rm rpi-5.10.y.tar.gz && \
    mv linux-rpi-5.10.y /usr/src/linux && \
    apt-get purge -y wget && \
    apt-get autoremove -y && \
    apt-get clean

# Copy the entire project code into the container
COPY . /app

# Add cron jobs to run Django management commands
RUN echo "*/2 * * * * export PYTHONPATH=/app && cd /app && /usr/local/bin/python manage.py update_pdr" > /etc/cron.d/update_commands && \
    echo "*/5 * * * * export PYTHONPATH=/app && cd /app && /usr/local/bin/python manage.py update_node_status" >> /etc/cron.d/update_commands && \
    chmod 0644 /etc/cron.d/update_commands && \
    crontab /etc/cron.d/update_commands && \
    touch /var/log/update_pdr.log /var/log/update_node_status.log

# Specify the port where the Django app will run (you can adjust this as needed)
EXPOSE 80

# Start cron service and run Django application
CMD service cron start && python manage.py runserver 0.0.0.0:80
