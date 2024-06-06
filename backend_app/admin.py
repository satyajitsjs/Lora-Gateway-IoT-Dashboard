from django.contrib import admin

# Register your models here.

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

@admin.register(DeviceModel)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'deviceId', 'time' , 'send_data' , 'size']
    ordering = ('-id',)


@admin.register(GatewayModel)
class GatewayAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'ip_address' ,'frequency']
    ordering = ('id',)


@admin.register(NodeModel)
class NodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'frequency', "p_d_r"  , "node_type" , 'gateway' , "publish_id" ,"status", "is_blocked"]
    ordering = ('id',)


@admin.register(MqttModel)
class MqttAdmin(admin.ModelAdmin):
    list_display = ['id' , 'ip_address' , 'port' , 'username' , 'password']
    ordering = ('id',)



@admin.register(NodeDataModel)
class NodeDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'NodeId', 'time' , 'counter', 's_n_r', 'r_s_s_i', 'c_r_c','node_status']
    list_filter = ['NodeId', 'time', 'c_r_c']
    ordering = ('id',)


@admin.register(authToken)
class authTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'access_token', 'refresh_token' , 'user']



@admin.register(GatewayIdModel)
class GatewayIdAdmin(admin.ModelAdmin):
    list_display = ["gateway_id"]



@admin.register(PublishTopic)
class publishAdmin(admin.ModelAdmin):
    list_display = ["node_id","publish_id","status"]
