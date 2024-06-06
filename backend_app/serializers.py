from rest_framework import serializers
from django.contrib.auth.models import User
from backend_app.models import (
    DeviceModel,
    GatewayModel, 
    NodeModel, 
    MqttModel,
    NodeDataModel,
    authToken,
    PublishTopic,
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password','first_name', 'last_name', 'date_joined')




class DeviceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceModel
        # fields = ['deviceId', 'time', 'snr', 'rssi']
        fields = "__all__"



class GatewayModelSerializer(serializers.ModelSerializer):
    bandwidth_display = serializers.CharField(source='get_BandWidth_display', read_only=True)
    gateway_type_display = serializers.CharField(source='get_Gateway_Type_display', read_only=True)

    class Meta:
        model = GatewayModel
        fields = '__all__'
        


class NodeSerializer(serializers.ModelSerializer):
    node_type_display = serializers.CharField(source='get_node_type_display', read_only=True)
    gateway_name = serializers.CharField(source='gateway.name', read_only=True)
    publish_id = serializers.CharField(source='get_publish_id', read_only=True)
    class Meta:
        model = NodeModel
        fields = '__all__'
    


class MQttSerializer(serializers.ModelSerializer):
    class Meta:
        model = MqttModel
        fields = '__all__'


class NodeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeDataModel
        fields = '__all__'


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = authToken
        fields = ['user', 'access_token', 'refresh_token']


class PublishTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublishTopic
        fields = '__all__'