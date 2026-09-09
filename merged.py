from __future__ import annotations

__author__ = "Elise Katsube"
__version__ = "23/07/26"

import paho.mqtt.client as mqtt
import matlab.engine
import json
import config
import time
import pprint

packet_count = 0

#MQTT setup ==================================================
client = mqtt.Client()
client.username_pw_set(config.USERNAME, config.PASSWORD)
client.tls_set()
print("Connecting...")
client.connect(config.BROKER, config.PORT) 
print("Connected!")
client.subscribe(config.CORRECTION_TOPIC_TEST) 
print("Subscribed to correction topic")

#MATLAB setup ===============================================
print("Starting MATLAB")

eng = matlab.engine.start_matlab()

eng.addpath(
    r"C:\Users\elise\OneDrive\Desktop\TeamSpace\My Tests",
    nargout=0
)

print("MATLAB read!")

#When file is ran this function is called message ==============
def start():
    #send message request to Elise
    first_message = {"packet_type":"message request"}
    first_json_message = json.dumps(first_message)

    print("Sending message request")
    client.publish(config.TELEMETRY_TOPIC_TEST, first_json_message)
    client.on_message = on_message
    client.loop_forever()

#Getting correction messages from Elise ==============================
def on_message(client, userdata, msg):
    try:
        json_dict = json.loads(msg.payload.decode()) #this could throw an error if not the proper format
        #the above json function converts string back to dictionary
        print("Received correction")
        route_packet(json_dict) #routes correction to function that makes calcs

    except Exception as e:
        print("Bad packet:", e)

# Packet counter
packet_count = 0

# 6. Continuous Loop receiving data from MATLAB and sending to HiveMQ
def to_MATLAB(data) -> dict:
    #print("Sending correction to MATLAB:")

    telemetry = eng.CubeSat(data, nargout=1)
    telemetry = json.loads(eng.jsonencode(telemetry))

    return telemetry

#Corrections received send to other functinons for calculations ==========
def route_packet(data):
    if (data.get("packet_type")=="message reply"):
        pprint.pprint(data)
        print("Received message reply...sending telemetry data...")
        time.sleep(4)
        intial_packet = {"packet_type": "initialize"}
        route_back(to_MATLAB(intial_packet)) #send the first round of data
        return
    elif (data.get("packet_type")!="correction"):
        print("ERROR: Received non-correction packet")
        return
    else:
        #pprint.pprint(data) #prints the corrections from Elise
        route_back(to_MATLAB(data)) #routes packet back to Elise
        
        # Send the correction back to MATLAB
        # json_str = json.dumps(data)
    return



def route_back(telemetry: dict):
    pprint.pprint(telemetry) #prints telemetry you send to me
    json_message = json.dumps(telemetry) #convert to json string

    client.publish(config.TELEMETRY_TOPIC_TEST, json_message)


if __name__ == "__main__":
    start()


