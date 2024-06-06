# tasks.py
from celery import Celery
from backend_app.management.commands.mqtt_publish import Command
from django.core.management import call_command

app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task
def mqtt_publish_task(topics):
    try:
        # Run the MQTT publish command
        call_command('mqtt_publish', *topics)
    except Exception as e:
        print(f"Error in MQTT publish task: {e}")

@app.task
def stop_mqtt_publish_task():
    try:
        # Stop the MQTT publish threads
        Command.stop_event.set()
    except Exception as e:
        print(f"Error in stop MQTT publish task: {e}")
