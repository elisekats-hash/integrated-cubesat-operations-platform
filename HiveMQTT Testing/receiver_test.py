import paho.mqtt.client as mqtt
import string
import json
import config
import pprint

#setup
client = mqtt.Client()
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

#msg.payload.decode contains the JSON file from elise

#this function routes the data received into the proper functions to
#deal with the data
def route_packet(data):
    if (data.get("packet_type")!="correction"):
        print("ERROR: Received non-telemetry packet")
        return
    pprint.pprint(data)

client.on_message = on_message

client.loop_forever()