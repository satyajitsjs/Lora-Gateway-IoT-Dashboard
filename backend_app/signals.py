# backend_app/signals.py
print("Signals file loaded successfully...........")
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NodeDataModel
import time
from .utils import UtilFunctions
@receiver(post_save, sender=NodeDataModel)
def handle_node_data_model_save(sender, instance, created, **kwargs):
    print("Signal handler for NodeDataModel post_save connected successfully.............")
    if created:
        try:
            UtilFunctions.publish_data(instance)
        except Exception as e:
            print(f"Error : {str(e)}")
