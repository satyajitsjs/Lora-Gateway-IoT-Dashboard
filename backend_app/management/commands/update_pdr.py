from django.core.management.base import BaseCommand
from backend_app.models import NodeModel

class Command(BaseCommand):
    help = 'Update PDR values for all NodeModels'

    def handle(self, *args, **options):
        node_models = NodeModel.objects.filter(status = True)
        for node_model in node_models:
            node_model.update_pdr()
            self.stdout.write(self.style.SUCCESS(f'Updated PDR for Node {node_model.id}'))
