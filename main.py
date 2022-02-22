import network
from umqtt.simple import MQTTClient

#Connect to WIFI

ssid = "57xxIoT"
password =  "jx+h2:s^4;)e)r-;+8[e3[39(rq5]>0_.(};)gu@3&nkn&d$2,gr,@o{{&g?"

station = network.WLAN(network.STA_IF)
 
if station.isconnected() == True:
  print("Already connected")
 
station.active(True)
station.connect(ssid, password)
 
while station.isconnected() == False:
  pass
 
print("Connection successful")
print(station.ifconfig())

MQTT_GO = False
#Publish dummy data to Cayenne
if MQTT_GO == True:
  mqtt_user = "3c13f910-7be2-11ec-a681-73c9540e1265"
  mqtt_pass = "82a57b8c82428e44a53da22c789da2faec6b32bc"
  mqtt_client_id = "e2d9a7d0-934e-11ec-8c44-371df593ba58"
  mqtt_server = "mqtt.mydevices.com"
  mqtt_port = 1883
  mqtt_topic = b"v1/" + mqtt_user + "/things/" + mqtt_client_id + "/data/json"

  client = MQTTClient(mqtt_client_id, mqtt_server, port=mqtt_port, user=mqtt_user, password=mqtt_pass)
  client.connect()
  temp_value = 22.55
  mqtt_msg = '[ { "channel": 1, "value": %s, "type": "temp", "unit": "c" } ]' % (temp_value)

  print(mqtt_topic)
  print(mqtt_msg)

  client.publish(mqtt_topic, mqtt_msg)

