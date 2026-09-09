from __future__ import annotations

__author__ = "Elise Katsube"
__version__ = "3/07/26"

import paho.mqtt.client as mqtt 
import json
import config 
import navigation as nav 
import health as health 
import pprint #to print dictionary but might need own function
import time

#need to save the data to send to gui
latest_packet = {} #may need to intiailize some stuff here
prev_packet = {} #ts not working idk man
num_packets = 0
_new_data = False

#setup
client = mqtt.Client()
client.username_pw_set(config.USERNAME, config.PASSWORD)
client.tls_set()

def on_message(client, userdata, msg):
    try:
        json_dict = json.loads(msg.payload.decode()) #this could throw an error if not the proper format
        #the above json function converts string back to dictionary
        route_packet(json_dict)

    except Exception as e:
        print("Bad packet:", e)

def route_packet(data:dict):
    global latest_packet
    global prev_packet
    global _new_data

    prev_packet = latest_packet
    latest_packet = data
    _new_data = True

    if (data.get("packet_type") == "message request"):
        print("Received message request")
        time.sleep(2)
        route_back({"packet_type":"message request"}, {"packet_type":"message reply"})
        return
    elif (data.get("packet_type")!="telemetry"):
        print("ERROR: Received non-telemetry packet")
        return
    else:
        #time.sleep(2)
        #pprint.pprint(data) # print out telemetry data received

        nav_commands = nav.process_telemetry(data)
        health_commands = health.process_telemetry(data)

        route_back(nav_commands, health_commands)
  
#send correction data back to David
def route_back(nav, health):
    """
    The route_back functions takes nav and health dictionaries as parameters. These contain
     corrections to send back.
    """
    if nav.get("packet_type") == "message request":
        #send message reply back
        json_message = json.dumps(health)
        print("Sending back message reply")
        time.sleep(2) #wait 8s before sending back a message reply to the request
        client.publish(config.CORRECTION_TOPIC_TEST, json_message)
    else:
        global num_packets
        num_packets += 1
        correction_dict = {"packet_type":"correction", "a_num_packets": num_packets}|nav|health
        pprint.pprint(correction_dict) #print out corrections
        json_message = json.dumps(correction_dict)

        #time.sleep(1) #delay the back and forth sending packets
        client.publish(config.CORRECTION_TOPIC_TEST, json_message)

def new_data() -> bool:
    global _new_data

    if _new_data:
        _new_data = False
        return True
    
    return False

def start():
    global latest_packet
    global prev_packet

    latest_packet = {
        "packet_type": "none",
        "position": {"x":0,"y":0,"z":0}
    }

    prev_packet = latest_packet

    client.on_message = on_message
    print("Connecting...")
    client.connect(config.BROKER, config.PORT)
    print("Connected!")

    client.subscribe(config.TELEMETRY_TOPIC_TEST)

    client.loop_start()