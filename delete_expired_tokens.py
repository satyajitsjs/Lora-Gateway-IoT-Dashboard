import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_server.settings')
django.setup()
from django.utils import timezone
from backend_app.models import authToken

def delete_expired_tokens():
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    authToken.objects.filter(created_at__lte=seven_days_ago).delete()

if __name__ == "__main__":
    delete_expired_tokens()
