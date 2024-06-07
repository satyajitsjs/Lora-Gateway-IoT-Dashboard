# utils.py or common_utils.py
import platform
import psutil
import time
from .management.mqtt.mqtt_script import MqttConnect
from django.conf import settings
import redis
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.utils import timezone
from backend_app.models import NodeDataModel,NodeModel
from multiprocessing import Process
from django.utils import timezone
from backend_app.models import authToken
class UtilFunctions:
    # print ColourFull message
    def print_colorful_message(self,message, color_code):
        """
        Print a colorful message to the console using ANSI escape codes.
        """
        print(f"\033[{color_code}m{message}\033[0m")
    


    def delete_expired_tokens(self):
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        authToken.objects.filter(created_at__lte=seven_days_ago).delete()
        self.print_colorful_message("Expired tokens deleted successfully","33")

        
    # Cpu Load Funciton
    def get_cpu_load():
        return psutil.cpu_percent(interval=1)


    # Cpu Temperature Funciton
    def get_cpu_temperature():
        if platform.system().lower() == 'linux':
            try:
                temperature_info = psutil.sensors_temperatures()
                if 'cpu_thermal' in temperature_info:
                    return temperature_info['cpu_thermal'][0].current
                else:
                    return None
            except Exception as e:
                print(f"Error getting temperature: {e}")
                return None
        else:
            print("Temperature monitoring is only supported on Linux.")
            return None

    # Publish the mqtt Data if some data save in database
    def publish_data(instance):
        r = redis.StrictRedis(host=settings.REDIS_HOST,port=settings.REDIS_PORT,password=settings.REDIS_PASSWORD,db=settings.REDIS_DB)
        is_publish = r.get("is_publish")
        if int(is_publish) == 1:
            mq = MqttConnect()
            mq.connect_to_broker()
            time.sleep(1)
            try:
                publish_id = instance.NodeId.publish_id.publish_id
                ACX = instance.ACX
                ACY = instance.ACY
                ACZ = instance.ACZ

                RPM_1 = instance.RPM_1
                RPM_2 = instance.RPM_2
                RPM_3 = instance.RPM_3
                RPM_4 = instance.RPM_4
                RPM_5 = instance.RPM_5

                times = instance.time
                times = times.strftime('%Y-%m-%d %H:%M:%S')
                mq.save_data_t_db_and_publish(
                    {"dataPoint": times, "paramType": 'ACX', "paramValue": ACX, "deviceId": publish_id})
                mq.save_data_t_db_and_publish(
                    {"dataPoint": times, "paramType": 'ACY', "paramValue": ACY, "deviceId": publish_id})
                mq.save_data_t_db_and_publish(
                    {"dataPoint": times, "paramType": 'ACZ', "paramValue": ACZ, "deviceId": publish_id})
                mq.save_data_t_db_and_publish(
                    {"dataPoint": times, "paramType": 'rpm_1', "paramValue": RPM_1, "deviceId": publish_id})
                mq.save_data_t_db_and_publish(
                    {"dataPoint": times, "paramType": 'rpm_2', "paramValue": RPM_2, "deviceId": publish_id})
                mq.save_data_t_db_and_publish(
                    {"dataPoint": times, "paramType": 'rpm_3', "paramValue": RPM_3, "deviceId": publish_id})
                mq.save_data_t_db_and_publish(
                    {"dataPoint": times, "paramType": 'rpm_4', "paramValue": RPM_4, "deviceId": publish_id})
                mq.save_data_t_db_and_publish(
                    {"dataPoint": times, "paramType": 'rpm_5', "paramValue": RPM_5, "deviceId": publish_id})
                mq.on_disconnect(None,None,1)
                time.sleep(1)
            except Exception as e:
                print(f"Error : {str(e)}")
        else:
            time.sleep(1)


    # Send Gateway status to user email
    def send_mail(self, subject, body_plain, body_html, receiver_email):
        sender_email = settings.SENDER_EMAIL
        smtp_server = settings.SMTP_SERVER
        smtp_port = settings.SMTP_PORT
        app_password = settings.APP_PASSWORD
        
        # Create a multipart message
        message = MIMEMultipart("alternative")
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        
        # Attach both plain text and HTML versions of the email body
        message.attach(MIMEText(body_plain, "plain"))
        message.attach(MIMEText(body_html, "html"))
        
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, app_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            self.print_colorful_message("Email sent successfully!", "32")
        except Exception as e:
            self.print_colorful_message(f"Error: {e}", "31")
    

    def notify_status(self, status, display_id, user):
        if status:
            subject = "Status Update: True"
            status_text = "True"
            status_color = "#27ae60"
        else:
            subject = "Status Update: False"
            status_text = "False"
            status_color = "#e74c3c"

        # Construct the HTML content with logo and styles
        body_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Status Update</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f5f5f5;
                        padding: 20px;
                    }}
                    .container {{
                        overflow: hidden;
                        font-family: Arial, sans-serif;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }}
                    h1 {{
                        color: #333333;
                        margin-bottom: 20px;
                    }}
                    p {{
                        color: #666666;
                        margin-bottom: 10px;
                    }}
                    .status {{
                        font-weight: bold;
                        font-style: italic;
                        color: {status_color};
                    }}
                    .user{{
                        font-weight: bold;
                        color: #666666;
                    }}
                    .footer {{
                        margin-top: 40px;
                        color: #999999;
                        font-size: 12px;
                    }}
                    .logo {{
                        float: left;
                        margin-right: 20px;
                        width: 80px; /* Adjust width as needed */
                        height: auto;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <img src="https://lora-bit.s3.amazonaws.com/Lora-Gateway/Logo.png" alt="Bariflo Logo" class="logo">
                    <div style="overflow: hidden;"> <!-- Added to contain the text -->
                        <h1>Status Update</h1>
                        <p>Hello <span class="user">{user.first_name}</span>,</p>
                        <p>This is a notification email regarding <span class="status">{display_id}</span>, the Gateway ID and its status.</p>
                        <p>The current status is: <span class="status">{status_text}</span></p>
                        <!-- Additional content -->
                        <p>We wanted to inform you that everything is going smoothly with your account.</p>
                        <p>If you have any questions or need further assistance, feel free to contact us.</p>
                        <p>Best regards,</p>
                        <p>The Team Bariflo</p>
                    </div>
                </div>
                <div class="footer">
                    This email was sent from MyApp. Please do not reply to this email.
                </div>
            </body>
            </html>
        """

        self.send_mail(subject, "", body_html, user.email)

