from django.core.management.base import BaseCommand
from django.utils import timezone
from backend_app.models import NodeDataModel,NodeModel
import redis


# Initialize Redis connection
redisLora = redis.Redis(host='98.70.76.242', port=6379, password="Bfl@2024#redis" ,decode_responses=True)

class Command(BaseCommand):
    help = 'Update node status based on last five minutes data'

    def handle(self, *args, **options):
        mode = redisLora.get("mode")
        if mode.lower() != "sleep":
            five_minutes_ago = timezone.now() - timezone.timedelta(minutes=1)
            nodes_with_status_true = NodeModel.objects.filter(status=True)

            for node in nodes_with_status_true:
                node_data = NodeDataModel.objects.filter(NodeId=node, time__gte=five_minutes_ago)
                node_status = node_data.exists()
                if not node_status:
                    node.status = False
                    node.save()

            self.stdout.write(self.style.SUCCESS('Node statuses updated successfully'))
        else:
            self.stdout.write(self.style.WARNING('Lora is in sleep Mode'))
