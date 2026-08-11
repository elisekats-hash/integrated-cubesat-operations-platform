import paho.mqtt.client as mqtt
import json
import config
import time
import random
import numpy as np
import pprint
import telemetry_test

#setup
client = mqtt.Client()
client.username_pw_set(config.USERNAME, config.PASSWORD)
client.tls_set()
print("Connecting...")
client.connect(config.BROKER, config.PORT)
print("Connected!")
client.subscribe(config.CORRECTION_TOPIC_TEST) 

num_packets = 0

#publish first message here
first_message = {"packet_type":"message request"}
first_json_message = json.dumps(first_message)

print("Sending message request")
client.publish(config.TELEMETRY_TOPIC_TEST, first_json_message)

def on_message(client, userdata, msg):
    try:
        json_dict = json.loads(msg.payload.decode()) #this could throw an error if not the proper format
        #the above json function converts string back to dictionary
        route_packet(json_dict)
        #call on function to puclish telemtry now
        #may need some timing here

    except Exception as e:
        print("Bad packet:", e)

#msg.payload.decode contains the JSON file from elise

#this function routes the data received into the proper functions to
#deal with the data
def route_packet(data):
    if (data.get("packet_type")=="message reply"):
        print("Received message reply...sending telemetry data...")
        telemetry_data = telemetry_test.tel_data(data)
        pprint.pprint({"packet_type": "telemetry"} | telemetry_data)

        route_back({"packet_type": "telemetry"} | telemetry_data) #send your telemetry data back to  me
        return
    elif (data.get("packet_type")!="correction"):
        print("ERROR: Received non-correction packet")
        
        return
    else:
        telemetry_data = telemetry_test.tel_data(data)

        route_back(telemetry_data)
        pprint.pprint(data)

def route_back(telemetry: dict):
    global num_packets
    num_packets += 1
    telemetry_dict = {"packet_type":"telemetry", "a_num_packets":num_packets}|telemetry
    json_message = json.dumps(telemetry_dict)

    client.publish(config.TELEMETRY_TOPIC_TEST, json_message)

client.on_message = on_message

client.loop_forever()