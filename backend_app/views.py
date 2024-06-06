from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
import psutil
import platform
import subprocess
from subprocess import PIPE
import re
import publish_scripts
import sys
import redis
import threading
from django.conf import settings
from load_control import control_load,control_network

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

from .models import (
    DeviceModel, 
    GatewayModel, 
    NodeModel,
    MqttModel,
    NodeDataModel,
    authToken,
    GatewayIdModel,
    PublishTopic,
)

from .serializers import (
    UserSerializer, 
    DeviceModelSerializer, 
    GatewayModelSerializer, 
    NodeSerializer,
    MQttSerializer,
    NodeDataSerializer,
    TokenSerializer,
    PublishTopicSerializer,
)

from backend_app.utils import UtilFunctions

def index(request):
    return render(request, "index.html")

# Genarate Token Function
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    access_token_lifetime = timedelta(days=1)
    access_token_expires_at = timezone.now() + access_token_lifetime
    return {
        'refresh_token': str(refresh),
        'access_token': str(refresh.access_token),
        'access_token_expires_at': access_token_expires_at.timestamp(),  # Include the expiration timestamp in the response
    }




# Login Function
@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user:
        token = get_tokens_for_user(user)
        token_data = {
            "user": user.id,
            "access_token": token['access_token'],
            "refresh_token": token['refresh_token']
        }
        token_serializer = TokenSerializer(data=token_data)
        
        if token_serializer.is_valid():
            token_serializer.save()  
            return JsonResponse({
                "Success": True,
                'message': 'Login successful',
                "token": token,
            })
        else:
            return JsonResponse({'message': 'Invalid token data', "Success": False , "Error":token_serializer.errors})
    else:
        return JsonResponse({'message': 'Invalid credentials', "Success": False})



# Function For Logout Api Which Delete the Token From the token Data Base
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    access_token = request.data.get('access_token')  # Use get() to avoid KeyError
    try:
        token = authToken.objects.get(access_token=access_token)
        token.delete()
        return Response({"message": "Logout successful"})
    except authToken.DoesNotExist:
        return Response({"error": "Token not found for the user"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

        
    
#  Get Token Funcion For check the token is match from localstorage or not
@api_view(['GET'])
def get_token(request):
    try:
        if request.method == "GET":
            token_instance = authToken.objects.all()
            serializer = TokenSerializer(token_instance , many = True)
            return JsonResponse({"token": serializer.data})
    except authToken.DoesNotExist:
        return JsonResponse({"Error": "Token not found for the user"}, status=404)
    except Exception as e:
        return JsonResponse({"Error": str(e)}, status=500)



# VIew the User By Token And Delete The User BY Token and Gateway id
@api_view(['GET' , 'POST'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response({"data": serializer.data})

    elif request.method == 'POST':
        try:
            gateway_id = request.data["id"]
            gateway = GatewayIdModel.objects.get(gateway_id=gateway_id)
            if gateway :
                serializer = UserSerializer(request.user)
                user_id = serializer.data["id"]
                user = User.objects.get(id=user_id)
                user.delete()
                return Response({"message": "User deleted successfully"})
        except KeyError:
            return Response({"error": "Missing 'id' in the request data."}, status=status.HTTP_400_BAD_REQUEST)
        except GatewayIdModel.DoesNotExist:
            return Response({"error": f"Gateway with id {gateway_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e :
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)





# Get and Update Function for user
@api_view(['GET', 'PUT' , 'PATCH'])
@permission_classes([IsAuthenticated])
def user_api_view(request, pk=None):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT','PATCH']:
        user_id = pk
        user = User.objects.get(pk=user_id)
        serializer = UserSerializer(user, data=request.data , partial=request.method == 'PATCH')

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Creat Device Function
@api_view(['POST' , 'GET'])
@permission_classes([IsAuthenticated])
def device_model_list_create_view(request):
    if request.method == 'POST':
        data = request.data
        DeviceModel.save_data(data)
        return Response({"message": "Data saved successfully."})
    elif request.method == "GET":
        try: 
            device_model = DeviceModel.objects.all()
            serializer = DeviceModelSerializer(device_model ,  many=True)
            return JsonResponse({"data":serializer.data})
        except Exception as e:
            return JsonResponse ({"Error" : str(e)})


# Get Device Function
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_model_retrieve_view(request, pk=None):
    queryset = DeviceModel.objects.all()
    device_model = generics.get_object_or_404(queryset, pk=pk)
    serializer = DeviceModelSerializer(device_model)
    return JsonResponse({"data":serializer.data})



# Get and Post function for GateWay
@api_view(['GET' , 'POST'])
@permission_classes([IsAuthenticated])
def gateway_model_list_create_view(request):
    if request.method == 'GET':
        selected_option = request.GET.get('type')
        if selected_option:
            queryset = GatewayModel.objects.filter(link_type=selected_option)
            serializer = GatewayModelSerializer(queryset, many=True)
            return JsonResponse({
                "data": serializer.data,
                'gateway_type_choices': GatewayModel.get_gateway_type_choices(),
                'bandwidth_choices': GatewayModel.get_bandwidth_choices(),
            })
        else:
            queryset = GatewayModel.objects.all()
            serializer = GatewayModelSerializer(queryset, many=True)
            return JsonResponse({
                "data": serializer.data,
                'gateway_type_choices': GatewayModel.get_gateway_type_choices(),
                'bandwidth_choices': GatewayModel.get_bandwidth_choices(),
            })

    elif request.method == 'POST':
        serializer = GatewayModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#Update Function For GetWay
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def gateway_model_retrieve_update_view(request, pk=None):
    gateway_model = get_object_or_404(GatewayModel, pk=pk)

    if request.method == 'GET':
        serializer = GatewayModelSerializer(gateway_model)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = GatewayModelSerializer(gateway_model, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Gateway details updated successfully", "data": serializer.data})
        return Response({"error": "Validation error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    


# Get And Post Function For Node
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def node_list_create(request):
    if request.method == 'GET':
        nodes = NodeModel.objects.filter(is_blocked = False)
        serializer = NodeSerializer(nodes, many=True)
        return Response({
            'data': serializer.data,
            'node_type_choices': NodeModel.get_node_type_choices(),
        })

    elif request.method == 'POST':
        serializer = NodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Get bY ID And Update function for node
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def node_retrieve_update(request, pk):
    try:
        node = NodeModel.objects.get(pk=pk)
    except NodeModel.DoesNotExist:
        return Response({"detail": "Node not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = NodeSerializer(node)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = NodeSerializer(node, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        node.delete()
        return Response({"detail": "Node deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



# Get Founciton for Get the Blocked Node 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def blocked_node_list(request):
    if request.method == 'GET':
        nodes = NodeModel.objects.filter(is_blocked=True)
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)



# Get And Post Fucntion for get the Mqtt Model and save the mqtt data
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def mqtt_list_create(request):
    if request.method == "POST":
        try:
            serializer = MQttSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({"message": "Mqtt Saved Successfully", "data": request.data})
        except Exception as e:
            return JsonResponse({"Serializer Error": str(serializer.errors), "Error": str(e)})

    elif request.method == "GET":
        mqtt = MqttModel.objects.all()
        serializer = MQttSerializer(mqtt, many=True)
        return Response(serializer.data)


# Get And PUT Fucntion for get the Mqtt Model and Update the mqtt data
@api_view(['GET', 'PUT' , 'PATCH'])
@permission_classes([IsAuthenticated])
def mqtt_retrieve_update(request ,pk):
    try:
        mqtt = MqttModel.objects.get(id=pk)
    except Exception as e:
        return Response({ "message" :  "Error" + str(e)} , status=status.HTTP_404_NOT_FOUND)
    
    if request.method == "GET":
        serializer = MQttSerializer(mqtt)
        return Response(serializer.data)
    elif request.method in ['PUT','PATCH']:
        serializer = MQttSerializer(mqtt, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message" : "Mqtt Updated SuccessFully" , "data":serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    
# Chnage Password Function for chaneg the password of admin
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method == 'POST':
        gateway_id = request.data['gateway-id']
        new_password = request.data['new-password']
        try :
            gateway = GatewayIdModel.objects.get(gateway_id = gateway_id)
            if gateway:
                user = request.user
                if user:
                    user.set_password(new_password)
                    user.save()
                    return JsonResponse({"message":"User Password Updated SuccessFully"})
        except Exception as e:
            return Response({"message":str(e)},status=status.HTTP_400_BAD_REQUEST)



# Get Function for All Node data
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def get_all_node_data(request):
    if request.method == 'GET':
        node_data = NodeDataModel.objects.filter(NodeId__status = True, NodeId__is_blocked = False)
        node_serializer = NodeDataSerializer(node_data,many=True)
        return JsonResponse({"data":node_serializer.data})


# Get Function for get node By It's Id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_node_by_nodeId(request,id):
    if request.method == 'GET':
        node_data = NodeDataModel.objects.filter(NodeId=id)
        node_serializer = NodeDataSerializer(node_data,many=True)
        return JsonResponse({"data":node_serializer.data})




# # Cpu Loard Fucntion
# def get_cpu_temperature():
#     if platform.system().lower() == 'linux':
#         try:
#             temperature_info = psutil.sensors_temperatures()
#             if 'cpu_thermal' in temperature_info:
#                 return temperature_info['cpu_thermal'][0].current
#             else:
#                 return None
#         except Exception as e:
#             print(f"Error getting temperature: {e}")
#             return None
#     else:
#         print("Temperature monitoring is only supported on Linux.")
#         return None


# Get Fucnton for get the System Details
@api_view(['GET'])
def system_details(request):
    try:
        if platform.system().lower() == 'linux':
            cpu_data = UtilFunctions.get_cpu_load()
            temperature_data = UtilFunctions.get_cpu_temperature()
        else:
            cpu_data = psutil.cpu_percent()
            temperature_data = None

        response_data = {
            'cpuLoad': cpu_data,
            'cpuTemperature': temperature_data,
        }

        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Get Function for Get the Wifi Details 
@api_view(['GET'])
def get_connected_wifi_details(request):
    try:
        wifi_names = None
        ip_address = None
        if platform.system().lower() == "linux":
            try:
                wifi_result = subprocess.check_output(['nmcli', 'connection', 'show', '--active'])
                wifi_result = wifi_result.decode('utf-8')
                wifi_names = parse_wifi_name(wifi_result)
                ip_result = subprocess.check_output(['nmcli', '-f', 'IP4.ADDRESS', 'device', 'show', 'wlan0'])  
                ip_result = ip_result.decode('utf-8')
                ip_address = parse_ip_address(ip_result)
            except Exception as e:
                print(str(e))
        return JsonResponse({"wifi_names": wifi_names, "ip_address": ip_address})
    except subprocess.CalledProcessError as e:
        return JsonResponse({"error": "Subprocess error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Get the Only Name Function
def parse_wifi_name(output):
    pattern = re.compile(r'\b(\w+)\s+[0-9a-f-]+\s+wifi\s+\w+\b')
    matches = pattern.findall(output)
    wifi_name = matches[0] if matches else None

    return wifi_name

# Get the Only ip address function
def parse_ip_address(result):
    lines = result.split('\n')
    for line in lines:
        if 'IP4.ADDRESS' in line:
            ip_address = line.split()[1]
            return ip_address
    return None



# All Wifi Network Show Function
@api_view(['GET'])
def list_all_wifi_networks(request):
    try:
        rescan_result = subprocess.run(['nmcli', 'device', 'wifi', 'rescan'], stdout=PIPE, stderr=PIPE, text=True)
        if rescan_result.returncode != 0:
            return Response({"error": rescan_result.stderr}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        list_result = subprocess.run(['nmcli', 'device', 'wifi', 'list'], stdout=PIPE, stderr=PIPE, text=True)
        if list_result.returncode == 0:
            wifi_names = parse_wifi_names(list_result.stdout)
            return JsonResponse({"wifi_names": wifi_names})
        else:
            return Response({"error": list_result.stderr}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except subprocess.CalledProcessError as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Get Only Wifi Name Function
def parse_wifi_names(output):
    lines = output.split('\n')
    unique_wifi_names = set()
    for line in lines:
        parts = line.split()
        if len(parts) >= 2 and parts[1] not in unique_wifi_names:
            unique_wifi_names.add(parts[1])

    return list(unique_wifi_names)


# Connect With Other wifi with its name and password function
@api_view(['POST'])
def connect_to_wifi(request):
    if request.method == 'POST':
        ssid = request.data.get('ssid')
        password = request.data.get('password')
        try:
            subprocess.check_call(['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password])
            return Response({"message": f"Connected to WiFi: {ssid} successfully."})
        except subprocess.CalledProcessError as e:
            return Response({"error": str(e.output)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)



# Execute a backend command by python finction
def execute_command(request):
    try:
        python_executable = sys.executable
        manage_py_path = 'C:/Users/embed/OneDrive/Desktop/Lora_GW/backend_server/manage.py'
        command = [python_executable, manage_py_path, 'runserver']
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
        print(result)
        return JsonResponse({'result': result})
    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': str(e)}, status=500)


# Post functionfor start publishing to Mqtt 
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def start_mqtt_publish(request):
#     if request.method == "POST":
#         topics = request.data.get('topics', [])
#         try:
#             publish_scripts.publish_data(*topics)
#             return JsonResponse({"message": "Published Successfully"})
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)


# # Stop function for stop the mqtt publishing
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def stop_mqtt_publish(request):
#     try:
#         publish_scripts.stop_publishing()
#         return JsonResponse({"message": "Stop command executed Successfully"})
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


class PublishTopicListCreateView(generics.ListCreateAPIView):
    queryset = PublishTopic.objects.all()
    serializer_class = PublishTopicSerializer

class PublishTopicRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PublishTopic.objects.all()
    serializer_class = PublishTopicSerializer


# Global variable to store the subprocess instance
mqtt_publish_process = None

def start_mqtt_publish_process(topics):
    global mqtt_publish_process,r
    
    try:
        gateway = GatewayModel.objects.filter().first()
        gateway_topic = gateway.publish_id
        if gateway_topic:
            topics.append(str(gateway_topic))

        for topic in topics:
            if str(topic) != str(gateway_topic):
                if not PublishTopic.objects.filter(publish_id=topic).exists():
                    return f"Topic '{topic}' is not assigned to any Node"

        if mqtt_publish_process:
            stop_mqtt_publish_process()

        command = ["python3", "-c", f"from publish_scripts import publish_data; publish_data(*{topics})"]
        mqtt_publish_process = subprocess.Popen(command)
        r.set("is_publish",1)
        
        return "Published Successfully"
    except Exception as e:
        return str(e)

def stop_mqtt_publish_process():
    global mqtt_publish_process
    
    try:
        if mqtt_publish_process and mqtt_publish_process.poll() is None:
            publish_scripts.stop_publishing()
            mqtt_publish_process.terminate()
            mqtt_publish_process.wait()  # Wait for the process to finish
            mqtt_publish_process = None
            r.set("is_publish",0)
        return "Mqtt Stop From Sending Message"
    except Exception as e:
        return str(e)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_mqtt_publish(request):
    if request.method == "POST":
        topics = request.data.get('topics', [])
        response = start_mqtt_publish_process(topics)
        if "error" in response:
            return JsonResponse({"error": response}, status=404)
        else:
            return JsonResponse({"message": response})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_mqtt_publish(request):
    if request.method == "POST":
        response = stop_mqtt_publish_process()
        return JsonResponse({"message": response})

'''
# Function to start MQTT publishing in a subprocess
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_mqtt_publish(request):
    global mqtt_publish_process
    
    if request.method == "POST":
        topics = request.data.get('topics', [])
        try:
            for topic in topics:
                try:
                    new_topic = PublishTopic.objects.get(publish_id=topic)
                    print(new_topic)
                except PublishTopic.DoesNotExist:
                    return JsonResponse({"error": f"Topic '{topic}' is not assigned to any Node"}, status=404)

            if mqtt_publish_process:
                stop_mqtt_publish(request)

            command = ["python3", "-c", f"from publish_scripts import publish_data; publish_data(*{topics})"]
            mqtt_publish_process = subprocess.Popen(command)
            
            return JsonResponse({"message": "Published Successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

# Function to stop the MQTT publishing subprocess
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_mqtt_publish(request):
    global mqtt_publish_process
    
    try:
        # Check if the process is running, if yes, terminate it
        if mqtt_publish_process and mqtt_publish_process.poll() is None:
            publish_scripts.stop_publishing()
            mqtt_publish_process.terminate()
            mqtt_publish_process.wait()  # Wait for the process to finish
            mqtt_publish_process = None
        return JsonResponse({"message": "Mqtt Stop From Sending Message"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
'''



# Function to get the status of the MQTT publishing subprocess
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_mqtt_publish_status(request):
    global mqtt_publish_process
    
    try:
        if mqtt_publish_process and mqtt_publish_process.poll() is None:
            status = "Running"
        else:
            status = "Not Running"
        return JsonResponse({"status": status})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



# Funciton For Lora Configuration with Node
subprocess_instance = None
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lora_configuration(request, id):
    global subprocess_instance
    if request.method == "GET":
        try:
            # Terminate the subprocess if it exists
            if subprocess_instance is not None and subprocess_instance.poll() is None:
                subprocess_instance.terminate()

            initial_key_c = "c"
            node_id = f"{id}"
            # Store the subprocess object
            subprocess_instance = subprocess.Popen(["python3", "-c", f"from lora_send_recive import main; main(initial_key='{initial_key_c}', node_id='{node_id}')"])

            return JsonResponse({'message': 'LoRa Configuration Started...'})
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"})



def start_lora_process():
    global subprocess_instance
    try:
        if subprocess_instance is not None and subprocess_instance.poll() is None:
            subprocess_instance.terminate()
            
        initial_key_c = "r"
        # Store the subprocess object
        subprocess_instance = subprocess.Popen(["python3", "-c", f"from lora_send_recive import main; main(initial_key='{initial_key_c}')"])
        return "LoRa process started."
    except Exception as e:
        return f"Error: {str(e)}"

def stop_lora_process():
    global subprocess_instance
    try:
        if subprocess_instance is not None and subprocess_instance.poll() is None:
            subprocess_instance.terminate()
        r.set("mode","Sleep")
        return "LoRa process stopped."
    except Exception as e:
        return f"Error: {str(e)}"

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lora_start_recive(request):
    if request.method == "GET":
        response = start_lora_process()
        return JsonResponse({'message': response})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lora_stop_recive(request):
    if request.method == "GET":
        response = stop_lora_process()
        return JsonResponse({'message': response})
        

"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lora_start_recive(request):
    global subprocess_instance
    if request.method == "GET":
        try:
            # Terminate the subprocess if it exists
            if subprocess_instance is not None and subprocess_instance.poll() is None:
                subprocess_instance.terminate()

            initial_key_c = "r"
            # Store the subprocess object
            subprocess_instance = subprocess.Popen(["python3", "-c", f"from lora_send_recive import main; main(initial_key='{initial_key_c}')"])

            return JsonResponse({'message': 'LoRa Started Now....'})
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"})




# Funciton For Stop Lora Process
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lora_stop_recive(request):
    global subprocess_instance
    if request.method == "GET":
        try:
            if subprocess_instance is not None and subprocess_instance.poll() is None:
                subprocess_instance.terminate()
                r.set("mode","Sleep")
            return JsonResponse({'message': 'LoRa Stop.....'})
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"})

"""
            
# Funciton For Get Lora Process Running Or Not 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lora_process(request):
    global subprocess_instance
    if request.method == "GET":
        try:
            if subprocess_instance is not None and subprocess_instance.poll() is None:
                return JsonResponse({'message': 'LoRa Activated', 'data': 'active'})
            else:
                return JsonResponse({'message': 'LoRa Not Activated', 'data': 'inactive'})
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"})
        

def get_lora_mode(request):
    try:
        global r
        mode = r.get("mode")
        return JsonResponse({"mode":mode})
    except Exception as e:
        return JsonResponse({"error":{str(e)}})


def start_initial():
    print("!!!!@Starting the initial function.............")
    try:
        publish_data = PublishTopic.objects.all()
        node = NodeModel.objects.filter(is_blocked=False)
        new_node = []
        for n in publish_data:
            new_node.append(n.publish_id)
        t1 = threading.Thread(target=start_mqtt_publish_process, args=(new_node,))  # Note the comma after the tuple
        t1.start()


        if node:
            t2 = threading.Thread(target=start_lora_process)
            t2.start()

        t1.join()
        if node:
            t2.join()
       
    except Exception as e:
        print(f"Error: {str(e)}")

