import paho.mqtt.client as mqtt
import string
import json
import config

import socket

# UDP connection to MATLAB
UDP_IP = "127.0.0.1"
# UDP_PORT = 5001  # different from sender's 5000
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(config.USERNAME, config.PASSWORD)
client.tls_set()
print("Connecting...")
client.connect(config.BROKER, config.PORT) 
print("Connected!")
client.subscribe(config.CORRECTION_TOPIC) 

#says whenever a message arrives, call the function on_message
print("Waiting for messages...")

def on_message(client, userdata, msg):
    try:
        json_dict = json.loads(msg.payload.decode()) #this could throw an error if not the proper format
        #the above json function converts string back to dictionary
        print("got the msg")
        route_packet(json_dict)

    except Exception as e:
        print("Bad packet:", e)

# msg.payload.decode contains the JSON file from elise

#this function routes the data received into the proper functions to
#deal with the data
def route_packet(data):
    print(data)
    packet_type = data.get("packet_type")

    #this are all EXAMPLES, packet_type is equiv to topic 


    if packet_type == "telemetry":
        #function to route the data to a specific function
        #nav.process_telemetry(data)

        print("packet is telemetry")

    elif (packet_type == "correction"):
        print("=== CORRECTION RECEIVED ===")
        for key, value in data.items():
            print(f"  {key}: {value}")
        print("===========================")
        
        # Send the correction back to MATLAB
        # json_str = json.dumps(data)
        # udp_sock.sendto(json_str.encode('utf-8'), (UDP_IP, UDP_PORT))
        # print("Correction forwarded to MATLAB!")
    else:
        print("Unknown packet")
    return

client.on_message = on_message

client.loop_forever()
