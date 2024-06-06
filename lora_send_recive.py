# lora_send_recive.py
import os
import sys
import time
import threading
from random import uniform
from LoRaRF import SX127x
from LoraGateDetails import LoraGateWaySending, LoraGateWayDownLink
from save_n_data_to_db import SaveNodeDataToDB
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad , pad
import json
from datetime import datetime
import redis
rdisLora = redis.Redis(host='localhost', port=6379, decode_responses=True)
rdisLora.set("mode","Sleep")



class LoRaCommunicationBase:
    def __init__(self):
        self.busId = 0
        self.csId = 0
        self.resetPin = 22
        self.irqPin = -1
        self.txenPin = -1
        self.rxenPin = -1
        self.LoRa = SX127x()
        self.SaveNodeDb = SaveNodeDataToDB()

class LoRaSender(LoRaCommunicationBase):
    def __init__(self, sending_gateway,node_id=None):
        super().__init__()
        self.sending_gateway = sending_gateway
        self.running = False
        self.stoping = False
        self.node_id = node_id


    def send_messages(self,args=None):  
        self.running = True

        frequency = self.sending_gateway.frequency
        bandwidth = self.sending_gateway.bandwidth
        payload_length = self.sending_gateway.payload_length
        crc = self.sending_gateway.crc
        code_rate = self.sending_gateway.code_rate
        
        encryption_key = str(self.sending_gateway.encripted_key)
        encryption_key = encryption_key.encode('utf-8')
        cipher = AES.new(encryption_key, AES.MODE_ECB)


        print("Begin LoRa radio")
        if not self.LoRa.begin(self.busId, self.csId, self.resetPin, self.irqPin, self.txenPin, self.rxenPin):
            raise Exception("Something wrong, can't begin LoRa radio")

        print(f"Set frequency to {frequency} Mhz")
        self.LoRa.setFrequency(int(frequency * 1000000))

        print("Set TX power to +17 dBm")
        self.LoRa.setTxPower(17, self.LoRa.TX_POWER_PA_BOOST)

        print(f"Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = {bandwidth} kHz\n\tCoding rate = {code_rate}")
        self.LoRa.setSpreadingFactor(7)
        self.LoRa.setBandwidth(bandwidth * 1000)
        self.LoRa.setCodeRate(code_rate)

        print(f"Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = {payload_length}\n\tCRC {crc}")
        self.LoRa.setHeaderType(self.LoRa.HEADER_EXPLICIT)
        self.LoRa.setPreambleLength(12)
        self.LoRa.setPayloadLength(payload_length)
        self.LoRa.setCrcEnable(crc)

        print("Set syncronize word to 0x34")
        self.LoRa.setSyncWord(0x34)

        print("\n-- LoRa Transmitter --\n")

        if args == "conf":
            rdisLora.set("mode","Conf")
            counter = 1
            while self.running:
                try:
                    message = self.sending_gateway.id
                    incripted_key = self.sending_gateway.encripted_key
                    frequency = self.SaveNodeDb.get_frequency(self.node_id)
                    send_msg =  f"{message}/{incripted_key}/{frequency}"
                    message_list = [ord(char) for char in send_msg]

                    self.LoRa.beginPacket()
                    self.LoRa.write(message_list, len(message_list))
                    self.LoRa.write([counter], 1)
                    self.LoRa.endPacket()

                    print(f"Message:{str(send_msg)} , Len:{len(send_msg)} , Counter : {counter}")
                    print(type(send_msg))

                    self.LoRa.wait()
                    
                    print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s \n".format(self.LoRa.transmitTime(), self.LoRa.dataRate()))

                    time.sleep(5)
                    if self.stoping:
                        self.running = False
                        self.LoRa.reset()
                        print("Sending Stop")
                        time.sleep(1)
                        break
                    counter += 1
                except Exception as e:
                    print(f"Error : {str(e)}")
                    self.LoRa.reset()
                    time.sleep(2)
                    continue
        rdisLora.set("mode","Tx")
        start_time = time.time()
        counter = 1
        while self.running:
            try:
                current_time = datetime.now()
                current_minute = current_time.minute
                if current_minute%2 != 0:
                    self.LoRa.reset()
                    time.sleep(1)
                    main("r")
                    print("Call the Recive.....")
                    break
                pub = self.SaveNodeDb.get_node_by_publish_id()
                for pub in pub:
                    node_id = pub.node_id.id
                    status = pub.status
                    message = f"{node_id}/{status}"
                    float_str = str(message)
                    # Convert float value to bytes
                    float_bytes = float_str.encode('utf-8')

                    encrypted_payload = cipher.encrypt(pad(float_bytes, AES.block_size))

                    message_list = [ord(char) for char in str(encrypted_payload)]

                    self.LoRa.beginPacket()
                    self.LoRa.write(message_list, len(message_list))
                    self.LoRa.write([counter], 1)
                    self.LoRa.endPacket()

                    print(f"{message}  {counter}")
                    print(type(message))

                    self.LoRa.wait()
                    
                    print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(self.LoRa.transmitTime(), self.LoRa.dataRate()))
                    
                    if time.time()-start_time >= 60:
                        time.sleep(1)
                        self.LoRa.reset()
                        time.sleep(1)
                        print("Stop Sending Now Recive Start ......")
                        main("r")
                        break
                    
                    if self.stoping:
                        self.running = False
                        self.LoRa.reset()
                        print("Sending Stop")
                        time.sleep(1)
                        break
                    time.sleep(5)
                    counter += 1

            except Exception as e:
                print(f"Error : {str(e)}")
                self.LoRa.reset()
                time.sleep(2)
                if time.time()-start_time >= 60:
                    time.sleep(1)
                    self.LoRa.reset()
                    time.sleep(1)
                    print("Stop Sending Now Recive Start ......")
                    main("r")
                    break
                continue
            
        



    def stop(self):
        self.running = False
        self.stoping = True


class LoRaReceiver(LoRaCommunicationBase):
    def __init__(self, receiving_gateway,node_id=None):
        super().__init__()
        self.receiving_gateway = receiving_gateway
        self.frequency_list = self.SaveNodeDb.get_frequency()
        self.running = False
        self.stoping = False
        self.node_id = node_id
        self.first_time = time.time()


    def receive_messages(self,args=None):
        self.running = True
        current_frequency_index = 0
        while self.running:
            time.sleep(1)
            frequency = self.receiving_gateway.frequency if args != None else self.frequency_list[current_frequency_index]
            bandwidth = self.receiving_gateway.bandwidth
            payload_length = self.receiving_gateway.payload_length
            crc = self.receiving_gateway.crc
            code_rate = self.receiving_gateway.code_rate

            encryption_key = str(self.receiving_gateway.encripted_key)
            encryption_key = encryption_key.encode('utf-8')
            cipher = AES.new(encryption_key, AES.MODE_ECB)

            print("\nBegin LoRa radio")
            if not self.LoRa.begin(self.busId, self.csId, self.resetPin, self.irqPin, self.txenPin, self.rxenPin):
                raise Exception("Something wrong, can't begin LoRa radio")

            print(f"Set frequency to {frequency} Mhz")
            self.LoRa.setFrequency(int(frequency * 1000000))

            print("Set RX gain to power saving gain")
            self.LoRa.setRxGain(self.LoRa.RX_GAIN_POWER_SAVING, self.LoRa.RX_GAIN_AUTO)

            print(f"Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = {bandwidth} kHz\n\tCoding rate = {code_rate}")
            self.LoRa.setSpreadingFactor(7)
            self.LoRa.setBandwidth(bandwidth * 1000)
            self.LoRa.setCodeRate(code_rate)

            print(f"Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = {payload_length}\n\tCRC {crc}")
            self.LoRa.setHeaderType(self.LoRa.HEADER_EXPLICIT)
            self.LoRa.setPreambleLength(12)
            self.LoRa.setPayloadLength(payload_length)
            self.LoRa.setCrcEnable(crc)

            print("Set syncronize word to 0x34")
            self.LoRa.setSyncWord(0x34)

            print("\n-- LoRa Receiver --\n")

            if args == "conf":
                rdisLora.set("mode","Conf")
                while self.running:
                    try:
                        self.LoRa.request()
                        self.LoRa.wait(20)
                        

                        message = ""
                        while self.LoRa.available() > 1:
                            message += chr(self.LoRa.read())
                        counter = self.LoRa.read()

                        print(f"{message}  {counter}")
                        print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(self.LoRa.packetRssi(), self.LoRa.snr()))
                        
                        if str(message) == str(self.node_id):
                            conf = self.SaveNodeDb.conf_node(message)
                            if conf == 1:
                                continue
                            elif conf == 0:
                                self.running = False 
                                self.LoRa.reset()
                                print("Node Not Registerd Going to Receive Mode In ..... 6 Sec\n")
                                for i in range(7):
                                    print(f"{i} Sec")
                                    time.sleep(1)
                                print("Start Reciving")
                                main("r")
                                break
                            else:
                                print("Already Activated Sending The Value in ..... 6 Sec\n")
                                for i in range(7):
                                    print(f"{i} Sec")
                                    time.sleep(1)
                                print("Start Sending \n")
                                continue

                        if self.stoping:
                            self.running = False 
                            self.LoRa.reset()
                            print("Recive Stop")
                            time.sleep(1)
                            break

                    except Exception as e:
                        print(f"Error:{str(e)}")
                        self.LoRa.reset()
                        time.sleep(2)
                        continue

            rdisLora.set("mode","Rx")
            start_time = time.time()
            while self.running:
                try:
                    current_time = datetime.now()
                    current_minute = current_time.minute
                    if current_minute%2 == 0:
                        self.LoRa.reset()
                        time.sleep(1)
                        main("s")
                        print("Call the send.....")
                        break

                    current_frequency_index = 0 if len(self.frequency_list) <= 1 else (current_frequency_index + 1) % len(self.frequency_list)
                    self.LoRa.request()
                    self.LoRa.wait(20)
                    time_wait = time.time()-start_time
                    if time_wait >= 20:
                        print("No data received in 20 seconds. Switching to the next frequency.")
                        self.LoRa.reset()
                        time.sleep(1)
                        if time.time()-self.first_time >= 60:
                            self.LoRa.reset()
                            time.sleep(1) 
                            print("Start Lora Sending Wait First.....")
                            main("s")
                            break
                        break

                    message = ""
                    while self.LoRa.available() > 1:
                        message += chr(self.LoRa.read())
                    counter = self.LoRa.read()
                    
                    try:
                        message = eval(message)
                        decrypted_message = unpad(cipher.decrypt(message), AES.block_size)
                        received_float = decrypted_message.decode('utf-8')
                        split_values = [val for val in received_float.split('/')]

                        ACX = float(split_values[0])
                        ACY = float(split_values[1])
                        ACZ = float(split_values[2])

                        RPM_1 = float(split_values[3])
                        RPM_2 = float(split_values[4])
                        RPM_3 = float(split_values[5])
                        RPM_4 = float(split_values[6])
                        RPM_5 = float(split_values[7])

                        node_id = str(split_values[8])
                        node_status = False if split_values[9] == "None" else split_values[9]

                        print(f"Node ID: {node_id}\n ACX: {ACX}\n ACY: {ACY}\n ACZ: {ACZ}\n RPM_1: {RPM_1}\n RPM_2: {RPM_2}\n RPM_3: {RPM_3}\n RPM_4: {RPM_4}\n RPM_5: {RPM_5}\n status:---{node_status}\n Counter: {counter}\n")
                    except Exception as e:
                        print(f"Error: {str(e)}, message: {message}, Counter: {counter}")
                        time.sleep(1)
                        continue


                    print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB \n".format(self.LoRa.packetRssi(), self.LoRa.snr()))
                    self.SaveNodeDb.update_node_to_active(node_id)
                    status = self.LoRa.status()
                    global c_r_c
                    c_r_c = True
                    if status == self.LoRa.STATUS_CRC_ERR : c_r_c = False ; print("CRC error")
                    elif status == self.LoRa.STATUS_HEADER_ERR : c_r_c = False ;  print("Packet header error")
                    time.sleep(1)
                    kwargs = {
                                "ACX":ACX,
                                "ACY":ACY,
                                "ACZ":ACZ,
                                "RPM_1":RPM_1,
                                "RPM_2":RPM_2,
                                "RPM_3":RPM_3,
                                "RPM_4":RPM_4,
                                "RPM_5":RPM_5,
                                "node_id":node_id,
                                "node_status":node_status,
                                "counter":counter,
                                "crc_value":c_r_c,
                                "snr_value":self.LoRa.snr(),
                                "rssi_value":self.LoRa.packetRssi(),
                            }

                    if message:
                            try:
                                self.SaveNodeDb.save_nodeData(**kwargs)
                                print("Save Data")
                                self.LoRa.reset()
                                time.sleep(1)
                                if time.time()-self.first_time >= 60:
                                    time.sleep(1)
                                    self.LoRa.reset()
                                    time.sleep(1)
                                    print("Start Lora Sending Last.....")
                                    main("s")
                                    break
                                break
                            except Exception as e:
                                print(str(e))
                                if time.time()-self.first_time >= 60:
                                    time.sleep(1)
                                    self.LoRa.reset()
                                    time.sleep(1)
                                    print("Start Lora Sending message_save.....")
                                    main("s")
                                    break
                                continue

                    
                    if self.stoping:
                        self.running = False 
                        self.LoRa.reset()
                        print("Recive Stop")
                        time.sleep(1)
                        break

                except Exception as e:
                    print(f"Error:{str(e)}")
                    if time.time()-self.first_time >= 60:
                        time.sleep(1)
                        self.LoRa.reset()
                        time.sleep(1)
                        print("Start Lora Sending message_save.....")
                        main("s")
                        break
                    continue
                
    def stop(self):
        self.running = False
        self.stoping = True





def main(initial_key="r",node_id=None):
    sending_gateway = LoraGateWaySending()
    receiving_gateway = LoraGateWayDownLink()

    receiver_thread = None
    sender_thread = None
    # ?timer_r = None  # Initialize timer_r object

    key = initial_key
    while True:
        try:
            if key == 'c':
                rdisLora.set("mode","Conf")
                # !Stop all running functions
                if receiver_thread and receiver_thread.is_alive():
                    receiver.stop()
                    receiver_thread.join()  # *Wait for receiver thread to finish
                if sender_thread and sender_thread.is_alive():
                    sender.stop()
                    sender_thread.join()  # *Wait for sender thread to finish
                
                # ?Cancel the timer_r if it's running
                # if timer_r and timer_r.is_alive():
                #     receiver.cancel()

                
                time.sleep(2)
                # !Start receiving for 10 seconds
                new_receiver = LoRaReceiver(receiving_gateway,node_id)
                new_receiver_thread = threading.Thread(target=new_receiver.receive_messages, args=("conf",))
                new_receiver_thread.start()
                timer_receive = threading.Timer(10, new_receiver.stop)
                timer_receive.start()
                new_receiver_thread.join()

                # !Start sending for 20 seconds
                new_sender = LoRaSender(sending_gateway,node_id)
                new_sender_thread = threading.Thread(target=new_sender.send_messages, args=("conf",))
                new_sender_thread.start()
                timer_send = threading.Timer(20, new_sender.stop)
                timer_send.start()
                new_sender_thread.join()

                # *Schedule 'r' key after 5 seconds
                timer_r = threading.Timer(5, lambda: main('r'))
                timer_r.start()

            elif key == 's':
                rdisLora.set("mode","Tx")
                if sender_thread and sender_thread.is_alive():
                    sender.stop()
                    sender_thread.join()
                if receiver_thread and receiver_thread.is_alive():
                    receiver.stop()
                    receiver_thread.join()

                # !Start a new sender thread
                sender = LoRaSender(sending_gateway)
                sender_thread = threading.Thread(target=sender.send_messages)
                sender_thread.start()

            elif key == 'r':
                rdisLora.set("mode","Rx")
                if sender_thread and sender_thread.is_alive():
                    sender.stop()
                    sender_thread.join()
                if receiver_thread and receiver_thread.is_alive():
                    receiver.stop()
                    receiver_thread.join()

                # !Start a new receiver thread
                receiver = LoRaReceiver(receiving_gateway)
                receiver_thread = threading.Thread(target=receiver.receive_messages)
                receiver_thread.start()

            key = input("Press 's' to send messages, 'r' to receive, 'c' to alternate between receiving and sending: \n")
        except KeyboardInterrupt:
            print("Stopping processes...")
            if sender_thread and sender_thread.is_alive():
                sender.stop()
                sender_thread.join()
            if receiver_thread and receiver_thread.is_alive():
                receiver.stop()
                receiver_thread.join()
            break


if __name__ == "__main__":
    main()
