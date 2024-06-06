from django.urls import path
from backend_app import views as v
from .views import PublishTopicListCreateView, PublishTopicRetrieveUpdateDestroyView 
from .views import start_initial
# from . import signals
urlpatterns = [
    # path('', v.index, name='index'),

    # User API views
    path('users/', v.user_api_view, name='user-api-view'),
    path('users/<int:pk>/', v.user_api_view, name='user-api-view'),

    # Authentication views
    path('login/', v.login_view, name='login-view'),
    path('logout/', v.logout_view, name='logout-view'),
    path('token/', v.get_token, name='get-token'),
    path('profile/', v.user_profile_view, name='user-profile-view'),

    # DeviceModel views
    path('device-models/', v.device_model_list_create_view, name='device-model-list-create-view'),
    path('device-models/<int:pk>/', v.device_model_retrieve_view, name='device-model-retrieve-view'),

    # GatewayModel views
    path('gateway-models/', v.gateway_model_list_create_view, name='gateway-model-list-create-view'),
    path('gateway-models/<str:pk>/', v.gateway_model_retrieve_update_view, name='gateway-model-retrieve-update-view'),

    # NodeModel views
    path('nodes/', v.node_list_create, name='node-list-create'),
    path('nodes/<str:pk>/', v.node_retrieve_update, name='node-retrieve-update'),
    path('block-nodes/', v.blocked_node_list, name='blocked-node-list'),

    # Execute any Command From Frontend
    path('execute-command/', v.execute_command, name='execute-command'),

    # Chnage MQtt
    path("mqtt/" , v.mqtt_list_create , name='mqtt-list-create'),
    path("mqtt/<int:pk>/" , v.mqtt_retrieve_update , name='mqtt-retrieve-update'),
    path("mqtt/publish/" , v.start_mqtt_publish , name='mqtt-data-publish'),
    path('mqtt/stop_publish/', v.stop_mqtt_publish, name='stop_mqtt_publish'),
    path('mqtt/get_publish_status/', v.get_mqtt_publish_status, name='get_mqtt_publish_status'),

    # Publish Data with Topic  
    path('publish-topics/', PublishTopicListCreateView.as_view(), name='publish-topic-list-create'),
    path('publish-topics/<int:pk>/', PublishTopicRetrieveUpdateDestroyView.as_view(), name='publish-topic-detail'),

    # Change Password
    path("change-password/" , v.change_password , name='change-password'),

    # GetNode Data
    path("nodes/data/<str:id>" , v.get_node_by_nodeId , name='node-data-id'),
    path("node/data/" , v.get_all_node_data , name='node-data'),

    # Get The CPU Details
    path("system/" , v.system_details , name='cpu-details'),


    # Get And Post For WIFI Connection
    path('connected_wifi/', v.get_connected_wifi_details, name='get_connected_wifi_details'),
    path('available_networks/', v.list_all_wifi_networks, name='list_all_wifi_networks'),
    path('connect_wifi/', v.connect_to_wifi, name='connect_to_wifi'),


    # Lora Configuration
    path('lora_configuration/<str:id>', v.lora_configuration, name='lora_configuration'),
    path('lora_start_recive/', v.lora_start_recive, name='lora_start_recive'),
    path('lora_stop_recive/', v.lora_stop_recive, name='lora_stop_recive'),
    path('get_lora_process/', v.get_lora_process, name='get_lora_process'),
    path('get_lora_mode/', v.get_lora_mode, name='get_lora_mode'),


]


import sys
if 'runserver' in sys.argv:
    start_initial()