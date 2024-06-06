import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_server.settings")  
django.setup()


from backend_app.models import NodeModel, NodeDataModel,PublishTopic
import random
from datetime import datetime
from backend_app.utils import UtilFunctions
from backend_app.management.mqtt.mqtt_script import MqttConnect
from backend_app.utils import UtilFunctions

class SaveNodeDataToDB:
    def save_nodeData(self,**kwargs):
        node = NodeModel.objects.get(id=kwargs["node_id"],status=True,is_blocked=False)
        counter = kwargs["counter"]
        crc_value = kwargs["crc_value"]
        snr_value = kwargs["snr_value"]
        rssi_value = kwargs["rssi_value"]
        ACX = kwargs["ACX"]
        ACY = kwargs["ACY"]
        ACZ = kwargs["ACZ"]
        RPM_1 = kwargs["RPM_1"]
        RPM_2 = kwargs["RPM_2"]
        RPM_3 = kwargs["RPM_3"]
        RPM_4 = kwargs["RPM_4"]
        RPM_5 = kwargs["RPM_5"]
        node_status = kwargs["node_status"]

        data_instance = NodeDataModel(
            NodeId=node,
            time= datetime.now(),
            counter= counter if kwargs["counter"] else 0 ,
            s_n_r= snr_value,
            r_s_s_i=  rssi_value,
            c_r_c= crc_value,
            ACX =  ACX, 
            ACY =  ACY, 
            ACZ =  ACZ, 
            RPM_1 =  RPM_1, 
            RPM_2 =  RPM_2, 
            RPM_3 =  RPM_3, 
            RPM_4 =  RPM_4, 
            RPM_5 =  RPM_5,
            node_status= node_status
        )
        
        try:
            data_instance.save()
            print(f"Data {counter} saved successfully with NodeId {node.id}.")
            UtilFunctions.publish_data(data_instance)
        except Exception as e:
            print("Error",str(e))


    def conf_node(self,id):
        try:
            node = NodeModel.objects.get(id=id, is_blocked=False)
            if node.status == False:
                node.status = True
                node.save()
                print("Node is Now Activate")
                return 1
        except NodeModel.DoesNotExist:
            print("Node not available or blocked.")
            return 0
        except Exception as e:
            print("Error:", str(e))
            


    def get_frequency(self,id=None):
        try:
            if id == None:
                node = NodeModel.objects.filter(is_blocked=False).exclude(node_type=5)
                frequency = []
                for n in node:
                    frequency.append(n.frequency)
                return frequency 
            node = NodeModel.objects.get(id=id)
            return(node.frequency)
        except NodeModel.DoesNotExist:
            print("Node not available or blocked.")
            return 0
        except Exception as e:
            print(f"Error : {str(e)}")
    

    def update_node_to_active(self,id):
        try:
            node = NodeModel.objects.get(id=id,is_blocked=False,status=False)
            node.status = True
            node.save()
            print("Node is Now Activate")
            return 1
        except NodeModel.DoesNotExist:
            print("Node not available or blocked.")
            return 0
        except Exception as e:
            print(f"Error : {str(e)}")


    def get_node_by_publish_id(self):
        try:
            node = PublishTopic.objects.all()
            return node
        except PublishTopic.DoesNotExist:
            return "Node Not Available"
        except Exception as e:
            return (str(e))
    
    def update_publish_status(self,publish_id,status):
        try:
            pub = PublishTopic.objects.get(publish_id=publish_id)
            print(pub.node_id.node_type)
            node_type = pub.node_id.node_type
            if node_type == 5:
                utif = UtilFunctions()
                utif.print_colorful_message(f"Node publish Status..... {status}","33")
                pass
            else:
                pub.status = status
                pub.save()
                print(pub.status)
        except Exception as e:
            print(f"Error:{str(e)}")

