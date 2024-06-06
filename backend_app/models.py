from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import pre_save
import redis
from django.core.exceptions import ValidationError
redisLora = redis.Redis(host='localhost', port=6379, decode_responses=True)


class DeviceModel(models.Model):
    deviceId = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)
    send_data = models.FloatField()
    size = models.IntegerField(default=0)

    @classmethod
    def save_data(cls, data):
        if cls.objects.count() >= 30:
            last_row = cls.objects.order_by('-time').last() 
            last_row.delete()
            print("Last Row Deleted")

        # previous_size = cls.objects.order_by('-time').first().size if cls.objects.exists() else 0
        # data["size"] = previous_size + data["size"]
        cls.objects.create(**data)


class GatewayIdModel(models.Model):
    gateway_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def save(self ,*args ,**kwargs):
        exicting_instace = GatewayIdModel.objects.first()

        if exicting_instace:
            raise ValidationError("Only one instance of GatewayIdModel is allowed.")
        else:
            super(GatewayIdModel, self).save(*args, **kwargs)

class GatewayModel(models.Model):
    GATEWAY_TYPE_CHOICE = [
        (1, 'X'),
        (2, 'Y'),
        (3, 'Z'),
    ]
    BANDWIDTH_CHOICE = [
        (1, 125),
        (2, 250),
        (3, 500),
    ]
    LINK_CHOICE = (
        ('DownLink', 'DownLink'),
        ('UpLink', 'UpLink'),
    )

    gateway = models.ForeignKey(GatewayIdModel , on_delete = models.CASCADE , default = None)
    name = models.CharField(max_length=255)
    link_type = models.CharField(max_length=20, choices=LINK_CHOICE, default='DownLink')
    ip_address = models.GenericIPAddressField()
    Gateway_Type = models.IntegerField(choices=GATEWAY_TYPE_CHOICE, default=1)
    frequency = models.FloatField()
    BandWidth = models.IntegerField(choices=BANDWIDTH_CHOICE, default=1)
    publish_id = models.IntegerField(default=0,null=True)
    s_f = models.IntegerField(
        validators=[
            MinValueValidator(6, message="SF must be greater than or equal to 6"),
            MaxValueValidator(12, message="SF must be less than or equal to 12"),
        ], default=7
    )
    t_x_power = models.IntegerField(
        validators=[
            MinValueValidator(17, message="Tx Power must be greater than or equal to 17"),
            MaxValueValidator(21, message="Tx Power must be less than or equal to 21"),
        ], default=18
    )
    r_x_gain = models.IntegerField(
        validators=[
            MinValueValidator(17, message="Rx Gain must be greater than or equal to 17"),
            MaxValueValidator(21, message="Rx Gain must be less than or equal to 21"),
        ], default=18
    )
    a_d_r = models.BooleanField(default=False)
    code_rate = models.IntegerField(
        validators=[
            MinValueValidator(4, message="ADR must be greater than or equal to 4"),
            MaxValueValidator(8, message="ADR must be less than or equal to 8"),
        ], default=5
    )
    payload_length = models.IntegerField(
        validators=[
            MinValueValidator(10, message="Payload Length must be greater than or equal to 10"),
            MaxValueValidator(20, message="Payload Length must be less than or equal to 8"),
        ], default=15
    )
    c_r_c = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_gateway_type_display(self):
        return dict(self.GATEWAY_TYPE_CHOICE).get(self.Gateway_Type, '')

    def get_bandwidth_display(self):
        return dict(self.BANDWIDTH_CHOICE).get(self.BandWidth, '')

    @classmethod
    def get_gateway_type_choices(cls):
        return cls.GATEWAY_TYPE_CHOICE

    @classmethod
    def get_bandwidth_choices(cls):
        return cls.BANDWIDTH_CHOICE
    
    def save(self, *args, **kwargs):
        existing_instances_count = GatewayModel.objects.filter(gateway=self.gateway).exclude(id=self.id).count()
        if existing_instances_count >= 2:
            raise ValidationError("Cannot create more than two instances for the GatewayModel.")
        super().save(*args, **kwargs)


@receiver(post_save, sender=GatewayModel)
def create_uplink_instance(sender, instance, created, **kwargs):
    """
    Signal handler to create an 'UpLink' instance when a 'DownLink' instance is saved.
    Restricts the creation to two instances (DownLink and UpLink) for the same GatewayIdModel.
    """
    if created and instance.link_type == 'DownLink':
        # Get the gateway_id from the related GatewayIdModel instance
        gateway_id = instance.gateway.gateway_id

        # Check if there are already two instances (DownLink and UpLink) for the same GatewayIdModel
        existing_instances_count = GatewayModel.objects.filter(gateway__gateway_id=gateway_id).count()

        if existing_instances_count < 2:
            # Create the 'UpLink' instance
            GatewayModel.objects.create(
                gateway_id=gateway_id,  # Set the gateway_id
                name=f"{instance.name} (UpLink)",
                link_type='UpLink',
                ip_address=instance.ip_address,
                Gateway_Type=instance.Gateway_Type,
                publish_id = instance.publish_id,
                frequency=instance.frequency+1,
                BandWidth=instance.BandWidth,
                s_f=instance.s_f,
                t_x_power=instance.t_x_power,
                r_x_gain=instance.r_x_gain,
                a_d_r=instance.a_d_r,
                code_rate=instance.code_rate,
                payload_length=instance.payload_length,
                c_r_c=instance.c_r_c
            )



class NodeModel(models.Model):
    NODE_TYPE_CHOICES = [
        (1, 'Type 1'),
        (2, 'Type 2'),
        (3, 'Type 3'),
        (4, 'Type 4'),
        (5, 'Type 5'),
    ]

    id = models.CharField(max_length=50, primary_key=True)
    frequency = models.FloatField(unique=True)
    status = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default = False)
    node_type = models.IntegerField(choices=NODE_TYPE_CHOICES, default=1)
    gateway = models.ForeignKey(GatewayModel, on_delete=models.CASCADE)
    p_d_r = models.CharField(max_length=100 , default = "0%")
    publish_id = models.OneToOneField('PublishTopic', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Node {self.id} (Gateway: {self.gateway.id})"
    
    
    def get_node_type_display(self):
        return dict(NodeModel.NODE_TYPE_CHOICES).get(self.node_type, "Unknown Type")
    

    @classmethod
    def get_node_type_choices(cls):
        return cls.NODE_TYPE_CHOICES
    
    def get_publish_id(self):
        return self.publish_id.publish_id if self.publish_id else None


    def update_pdr(self):
        """
        Calculate Packet Delivery Ratio (PDR) based on data received in the last minute.
        Automatically called every 1 minute.
        """
        one_minute_ago = timezone.now() - timezone.timedelta(minutes=2)
        data_records_last_minute = NodeDataModel.objects.filter(
            NodeId=self,
            time__gte=one_minute_ago
        )
        total_records_last_minute = 12
        successful_records_last_minute = data_records_last_minute.filter(c_r_c=True).count()
        if total_records_last_minute > 0:
            pdr_percentage = (successful_records_last_minute / total_records_last_minute) * 100
            self.p_d_r = f"{round(pdr_percentage, 2)}%"
            self.save()

class MqttModel(models.Model):
    ip_address = models.CharField(max_length = 30)
    port = models.IntegerField()
    username = models.CharField(max_length = 100)
    password = models.CharField(max_length = 100)

    def save(self ,*args ,**kwargs):
        exicting_instace = MqttModel.objects.exclude(pk=self.pk).first()

        if exicting_instace:
            raise ValidationError("Only one instance of MqttModel is allowed.")
        else:
            super(MqttModel, self).save(*args, **kwargs)


class NodeDataModel(models.Model):
    NodeId = models.ForeignKey(NodeModel, on_delete=models.CASCADE)
    time = models.DateTimeField(default=datetime.now)
    counter = models.IntegerField()
    s_n_r = models.CharField(max_length=100)
    r_s_s_i = models.CharField(max_length=100)
    c_r_c = models.BooleanField(default=True)
    ACX = models.FloatField(default=0.0)
    ACY = models.FloatField(default=0.0)
    ACZ = models.FloatField(default=0.0)
    RPM_1 = models.FloatField(default=0.0)
    RPM_2 = models.FloatField(default=0.0)
    RPM_3 = models.FloatField(default=0.0)
    RPM_4 = models.FloatField(default=0.0)
    RPM_5 = models.FloatField(default=0.0)
    node_status = models.BooleanField(default=False)


    class Meta:
        unique_together = ['NodeId', 'time']
        ordering = ['-time']

    def save(self, *args, **kwargs):
        existing_records_count = NodeDataModel.objects.filter(NodeId=self.NodeId).count()
        if existing_records_count >= 30:
            oldest_record = NodeDataModel.objects.filter(NodeId=self.NodeId).earliest('time')
            oldest_record.delete()

        super().save(*args, **kwargs)
    

    def __str__(self):
        return f"{self.id}'s NodeId is {self.NodeId}"


@receiver(post_save, sender=NodeDataModel)
def update_pdr_on_node_data_save(sender, instance, created, **kwargs):
    """
    Signal receiver to update PDR in NodeModel whenever NodeDataModel is saved.
    """
    if created:  # Only update PDR if a new NodeDataModel instance is created
        node = instance.NodeId  # Assuming NodeId is the ForeignKey field in NodeDataModel
        node.update_pdr()

class PublishTopic(models.Model):
    node_id = models.ForeignKey(NodeModel, on_delete=models.CASCADE)
    publish_id = models.CharField(max_length=50, unique=True)
    status = models.BooleanField(default=False)


@receiver(post_save, sender=PublishTopic)
def update_node_publish_id(sender, instance, created, **kwargs):
    if created:
        instance.node_id.publish_id = instance
        instance.node_id.save()


class authToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_tokens')
    access_token = models.CharField(max_length=250)
    refresh_token = models.CharField(max_length=250)
    created_at = models.DateTimeField(default=datetime.now)


