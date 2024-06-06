# from django.core.management.base import BaseCommand
# from backend_app.models import GatewayIdModel, GatewayModel,MqttModel
# import uuid

# class Command(BaseCommand):
#     help = 'Create GatewayIdModel and GatewayModel instances'

#     def handle(self, *args, **options):
#         # Check if a GatewayIdModel instance already exists
#         existing_gateway_id_instance = GatewayIdModel.objects.first()

#         if existing_gateway_id_instance:
#             self.stdout.write(self.style.WARNING('GatewayIdModel instance already exists. Skipping creation.'))
#         else:
#             # Create a new GatewayIdModel instance
#             new_gateway_id_instance = GatewayIdModel.objects.create(gateway_id=uuid.uuid4())
#             self.stdout.write(self.style.SUCCESS('GatewayIdModel instance created successfully.'))

#             # Create a corresponding GatewayModel instance
#             GatewayModel.objects.create(
#                 gateway=new_gateway_id_instance,
#                 name='Lora Gateway', 
#                 ip_address="192.168.0.148", 
#                 frequency=432.0
#             )
            
#             self.stdout.write(self.style.SUCCESS('GatewayModel instance created successfully.'))

#             MqttModel.objects.create(
#                 ip_address='4.240.114.7',
#                 port=1883,
#                 username='BarifloLabs',
#                 password='Bfl@123'
#             )

#             self.stdout.write(self.style.SUCCESS('MqttModel instance created successfully.'))


from django.core.management.base import BaseCommand
from backend_app.models import GatewayIdModel, GatewayModel, MqttModel
import uuid

class Command(BaseCommand):
    help = 'Create GatewayIdModel and GatewayModel instances'

    def add_arguments(self, parser):
        parser.add_argument('publish_id', type=int, help='Publish ID for the GatewayModel')

    def handle(self, *args, **options):
        publish_id = options['publish_id']

        # Check if a GatewayIdModel instance already exists
        existing_gateway_id_instance = GatewayIdModel.objects.first()

        if existing_gateway_id_instance:
            self.stdout.write(self.style.WARNING('GatewayIdModel instance already exists. Skipping creation.'))
        else:
            # Create a new GatewayIdModel instance
            new_gateway_id_instance = GatewayIdModel.objects.create(gateway_id=uuid.uuid4())
            self.stdout.write(self.style.SUCCESS('GatewayIdModel instance created successfully.'))

            # Create a corresponding GatewayModel instance with the provided publish ID
            GatewayModel.objects.create(
                gateway=new_gateway_id_instance,
                name='Lora Gateway', 
                ip_address="192.168.0.148", 
                frequency=432.0,
                publish_id=publish_id  # Use the provided publish ID
            )
            
            self.stdout.write(self.style.SUCCESS('GatewayModel instance created successfully.'))

            MqttModel.objects.create(
                ip_address='4.240.114.7',
                port=1883,
                username='BarifloLabs',
                password='Bfl@123'
            )

            self.stdout.write(self.style.SUCCESS('MqttModel instance created successfully.'))
