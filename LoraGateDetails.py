import os
import django
import psutil
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_server.settings")  
django.setup()

import uuid
from backend_app.models import GatewayModel

GatewayDetailsRecive = GatewayModel.objects.get(link_type = "DownLink")
GatewayDetailsSending = GatewayModel.objects.get(link_type = "UpLink")



class MacAddress:
    def __init__(self):
        self.mac_address = self.get_mac_address()

    def get_mac_address(self):
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
        return mac

class LoraGateWaySending(MacAddress):

    def __init__(self):
        super().__init__() 
        self.id = GatewayDetailsSending.gateway.gateway_id
        self.name = GatewayDetailsSending.name
        self.ip_address = GatewayDetailsSending.ip_address
        self.frequency = GatewayDetailsSending.frequency
        self.bandwidth = GatewayDetailsSending.get_bandwidth_display()
        self.sf = GatewayDetailsSending.s_f
        self.txPower = GatewayDetailsSending.t_x_power
        self.rxGain = GatewayDetailsSending.r_x_gain
        self.adr = GatewayDetailsSending.a_d_r
        self.code_rate = GatewayDetailsSending.code_rate
        self.payload_length = GatewayDetailsSending.payload_length
        self.crc = GatewayDetailsSending.c_r_c
        self.mac = self.mac_address
        self.encripted_key = str(self.mac)[:8] + str(self.id)[-8:]





class LoraGateWayDownLink(MacAddress):

    def __init__(self):
        super().__init__() 
        self.id = GatewayDetailsRecive.gateway.gateway_id
        self.name = GatewayDetailsRecive.name
        self.ip_address = GatewayDetailsRecive.ip_address
        self.frequency = GatewayDetailsRecive.frequency
        self.bandwidth = GatewayDetailsRecive.get_bandwidth_display()
        self.sf = GatewayDetailsRecive.s_f
        self.txPower = GatewayDetailsRecive.t_x_power
        self.rxGain = GatewayDetailsRecive.r_x_gain
        self.adr = GatewayDetailsRecive.a_d_r
        self.code_rate = GatewayDetailsRecive.code_rate
        self.payload_length = GatewayDetailsRecive.payload_length
        self.crc = GatewayDetailsRecive.c_r_c
        self.mac = self.mac_address
        self.encripted_key = str(self.mac)[:8] + str(self.id)[-8:]



