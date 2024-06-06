# publish_scripts.py
import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_server.settings")
django.setup()

from backend_app.models import (
    NodeDataModel,
    PublishTopic,
    NodeModel,
    GatewayModel,
    User
)
import redis
from backend_app.utils import UtilFunctions
from save_n_data_to_db import SaveNodeDataToDB
import threading
from backend_app.management.mqtt.mqtt_script import MqttConnect
from random import uniform
from datetime import datetime
import time
from paho.mqtt.client import Client
import json
from load_control import control_gateway

rdisLora = redis.Redis(host='localhost', port=6379, decode_responses=True)
redismode = rdisLora.get("mode")
# Global variable to signal the script to stop
stop_script = False
stop_lock = threading.Lock()
saveNode = SaveNodeDataToDB()


def stop_publishing():
    global stop_script
    with stop_lock:
        stop_script = True


def publish_data(*topics):
    print(topics)
    global stop_script
    mq = MqttConnect()
    mq.topic = topics
    mq._connected = True
    stop_script = False

    try:
        publish_thread = threading.Thread(target=post_data_to_publish, args=(mq,))
        subscribe_thread = threading.Thread(target=data_subscribe, args=(mq,))

        publish_thread.start()
        subscribe_thread.start()

        while True:
            try:
                time.sleep(1)
                with stop_lock:
                    if stop_script == True:
                        mq.on_disconnect(None, None, 1)
                        break
            except KeyboardInterrupt:
                with stop_lock:
                    stop_script = True
                    mq.on_disconnect(None, None, 1)
                    mq._client.disconnect()
                print("KeyboardInterrupt: Stopping threads gracefully...")
                break

        publish_thread.join()
        subscribe_thread.join()

    except Exception as e:
        print(f"An error occurred: {e}")

def post_data_to_publish(mq):
    mq.connect_to_broker()

    global redismode  # Make sure redismode is accessible globally

    while True:
        with stop_lock:
            if stop_script:
                break

        if not mq.is_connected():  # Check if MQTT client is connected
            print("Not connected to the broker. Skipping publishing.")
            time.sleep(5)
            continue

        redismode = rdisLora.get("mode")  # Get redismode value

        gateway = GatewayModel.objects.filter().first()
        gateway_topic = gateway.publish_id
        for i in mq.topic:
            if str(i) == str(gateway_topic):
                cpu_temp = UtilFunctions.get_cpu_temperature()
                times = datetime.now()
                times = times.strftime('%Y-%m-%d %H:%M:%S')
                mq.data_publish({"dataPoint": times, "paramType": 'cpu_temp', "paramValue": cpu_temp, "deviceId": i})
        time.sleep(10)


def on_connect(client, userdata, flags, rc):
    print('Connected with result code '+str(rc))


def on_sub_message(client, userdata, message):
    global status
    data = json.loads(message.payload.decode('utf-8'))
    status = data["status"]
    display_id = data["display_id"]
    gateway = GatewayModel.objects.filter().first()
    gateway_topic = gateway.publish_id
    user = User.objects.get()
    if str(display_id) == str(gateway_topic):
        if str(status).lower() == "true":
            control_gateway("start")
        else:
            control_gateway("stop")
        utilsfun = UtilFunctions()
        utilsfun.notify_status(status,display_id,user)
    else:
        saveNode.update_publish_status(display_id, status)
    print(f"Received message: {data}")
    print(f"status val: ---{status}")


def data_subscribe(mq):
    mqtt_client = Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_sub_message
    mqtt_client.username_pw_set(mq._username, password=mq._password)
    mqtt_client.connect(mq._mqttBroker, port=mq._port)
    mqtt_client.loop_start()

    try:
        for t in mq.topic:
            mqtt_client.subscribe(t)
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Stopping subscribe thread gracefully...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    except Exception as e:
        print(f"Error:{str(e)}")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


# def post_data_to_publish_new(*topics):
#     mq = MqttConnect()
#     mq.topic = topics
#     mq.connect_to_broker()

#     global redismode  # Make sure redismode is accessible globally

#     while True:
#         with stop_lock:
#             if stop_script:
#                 break

#         if not mq.is_connected():  # Check if MQTT client is connected
#             print("Not connected to the broker. Skipping publishing.")
#             time.sleep(5)
#             continue

#         redismode = rdisLora.get("mode")  # Get redismode value

#         gateway = GatewayModel.objects.filter().first()
#         gateway_topic = gateway.publish_id
#         for i in mq.topic:
#             if str(i) == str(gateway_topic):
#                 cpu_temp = UtilFunctions.get_cpu_temperature()
#                 times = datetime.now()
#                 times = times.strftime('%Y-%m-%d %H:%M:%S')
#                 mq.data_publish({"dataPoint": times, "paramType": 'cpu_temp', "paramValue": cpu_temp, "deviceId": i})
#             else:
#                 try:
#                     publish_id = PublishTopic.objects.get(publish_id=i)
#                     node = NodeModel.objects.get(publish_id=publish_id, status=True, is_blocked=False)
#                     NodeData = NodeDataModel.objects.filter(NodeId=node.id).first()
#                     ACX = NodeData.ACX
#                     ACY = NodeData.ACY
#                     ACZ = NodeData.ACZ

#                     RPM_1 = NodeData.RPM_1
#                     RPM_2 = NodeData.RPM_2
#                     RPM_3 = NodeData.RPM_3
#                     RPM_4 = NodeData.RPM_4
#                     RPM_5 = NodeData.RPM_5

#                     times = NodeData.time
#                     times = times.strftime('%Y-%m-%d %H:%M:%S')
#                     mq.save_data_t_db_and_publish({"dataPoint": times, "paramType": 'ACX', "paramValue": ACX, "deviceId": i})
#                     mq.save_data_t_db_and_publish({"dataPoint": times, "paramType": 'ACY', "paramValue": ACY, "deviceId": i})
#                     mq.save_data_t_db_and_publish({"dataPoint": times, "paramType": 'ACZ', "paramValue": ACZ, "deviceId": i})
#                     mq.save_data_t_db_and_publish({"dataPoint": times, "paramType": 'rpm_1', "paramValue": RPM_1, "deviceId": i})
#                     mq.save_data_t_db_and_publish({"dataPoint": times, "paramType": 'rpm_2', "paramValue": RPM_2, "deviceId": i})
#                     mq.save_data_t_db_and_publish({"dataPoint": times, "paramType": 'rpm_3', "paramValue": RPM_3, "deviceId": i})
#                     mq.save_data_t_db_and_publish({"dataPoint": times, "paramType": 'rpm_4', "paramValue": RPM_4, "deviceId": i})
#                     mq.save_data_t_db_and_publish({"dataPoint": times, "paramType": 'rpm_5', "paramValue": RPM_5, "deviceId": i})
#                 except Exception as e:
#                     print(f"Error : {str(e)}")
#                     continue
#         time.sleep(10)

# if __name__ == "__main__":
#     topics_to_publish = ['']
#     post_data_to_publish_new(*topics_to_publish)
