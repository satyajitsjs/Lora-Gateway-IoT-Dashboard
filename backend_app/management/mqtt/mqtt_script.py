# mqtt_script.py

from paho.mqtt.client import Client
import json
from datetime import datetime
from backend_app.models import MqttModel , DeviceModel


class MqttConnect:
    def __init__(self):
        self.topic = []
        self._connected = False
        self._client = Client()
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._client.on_log = self.log_message
        self._client.on_disconnect = self.on_disconnect
        self._client.connect_fail_callback = self.connect_fail_callback
        mqtt_model_data = MqttModel.objects.first()
        if mqtt_model_data:
            self._mqttBroker = mqtt_model_data.ip_address
            self._port = mqtt_model_data.port
            self._username = mqtt_model_data.username
            self._password = mqtt_model_data.password
        else:
            self._mqttBroker = "4.240.114.7"
            self._port = 1883
            self._username = "BarifloLabs"
            self._password = "Bfl@123"

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connection result: {rc}")
        if rc == 0:
            print("Client Is Connected")
            self._connected = True
            for t in self.topic:
                self._client.subscribe(t)
        else:
            print("Connection Failed")
            self._client.reconnect()  
    

    def is_connected(self):
        return self._connected



    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected {rc}")
        self._connected = False
        if rc == 7 or rc == 1:  # rc == 1 indicates a manual disconnection
            print("Manual disconnection. Avoiding automatic reconnection.")
        else:
            try:
                self._client.reconnect()
            except Exception as e:
                print(f"Error during reconnection: {e}")



    def connect_fail_callback(self, userdata, flags, rc):
        print("Connection failed:", rc)
        self._connected = False


    def log_message(self, client, userdata, level, buf):
        try:
            print("log: " + buf)
        except Exception as e:
            print("Error" + str(e))


    def on_message(self, client, userdata, message):
        print("message: " + str(message.payload.decode("utf-8")))


    def connect_to_broker(self):
        try:
            self._client.username_pw_set(self._username, self._password)
            self._client.connect(self._mqttBroker, port=self._port)
            self._client.loop_start()
        except Exception as e:
            print(f"Error during connection: {e}")


    def data_publish(self, publish_data):
        if self._connected == False:
            print("Not connected to the broker.")
            return
        publish_topic = publish_data["deviceId"]
        publish_data = json.dumps(publish_data)
        self._client.publish(publish_topic + "/data", publish_data)
        print(f"Just published {str(publish_data)} to {publish_topic}")
    
    
    def open_file(self , file_name):
        if file_name.lower().endswith(".json"):
            with open(file_name) as json_file:
                data = json.load(json_file)
            return data
    

    def save_data_t_db_and_publish(self, publish_data):
        if self._connected == False:
            print("Not connected to the broker.")
            return

        publish_topic = publish_data["deviceId"]
        publish_data_str = json.dumps(publish_data)

        self._client.publish(publish_topic + "/data", publish_data_str)

        publish_data_dict = json.loads(publish_data_str)
        data = {
            "deviceId": publish_data_dict["deviceId"],
            "time": publish_data_dict["dataPoint"],
            "send_data": publish_data_dict["paramValue"],
            "size": publish_data_dict.__sizeof__()
        }
        DeviceModel.save_data(data)
        print(f"Just published {str(publish_data)} to {publish_topic}")


