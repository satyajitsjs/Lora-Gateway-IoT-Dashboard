import RPi.GPIO as GPIO
import time
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def control_gateway(command, led_pin=23):
    GPIO.setup(led_pin, GPIO.OUT)
    if command == 'start':
        GPIO.output(led_pin, GPIO.HIGH)
    elif command == 'stop':
        GPIO.output(led_pin, GPIO.LOW)
    else:
        print("Invalid input. Please enter '1' to turn the LED on or '2' to turn it off.")

def control_network(led_pin=6):
    GPIO.setup(led_pin, GPIO.OUT)
    while True:
        GPIO.output(led_pin, GPIO.HIGH)
        time.sleep(3600)
        GPIO.output(led_pin, GPIO.LOW)
        time.sleep(5)

def control_load(led_pin=5):
    GPIO.setup(led_pin, GPIO.OUT)
    while True:
        GPIO.output(led_pin, GPIO.HIGH)
        time.sleep(1800)
        GPIO.output(led_pin, GPIO.LOW)
        time.sleep(1800)

if __name__ == "__main__":
    # Create threads for control_network and control_load
    network_thread = threading.Thread(target=control_network)
    load_thread = threading.Thread(target=control_load)

    # Start the threads
    network_thread.start()
    load_thread.start()

    # Join the threads (wait for them to finish if needed)
    network_thread.join()
    load_thread.join()

    GPIO.cleanup()
