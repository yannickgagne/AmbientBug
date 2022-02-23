import time
import json
import network
from umqtt.simple import MQTTClient
from machine import Pin, I2C
import ahtx0

last_tick = 0
pub_delay_ms = 60000

#Sensor setup
i2c = I2C(scl=Pin(5), sda=Pin(4))
sensor = ahtx0.AHT20(i2c)
time.sleep_ms(20)

#MQTT Cayenne setup
mqtt_user = "3c13f910-7be2-11ec-a681-73c9540e1265"
mqtt_pass = "82a57b8c82428e44a53da22c789da2faec6b32bc"
mqtt_client_id = "e2d9a7d0-934e-11ec-8c44-371df593ba58"
mqtt_server = "mqtt.mydevices.com"
mqtt_port = 1883
mqtt_topic = b"v1/" + mqtt_user + "/things/" + mqtt_client_id + "/data/json"
client = MQTTClient(mqtt_client_id, mqtt_server, port=mqtt_port, user=mqtt_user, password=mqtt_pass)

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

MQTT_GO = True
#Publish dummy data to Cayenne
if MQTT_GO == True:
  client.connect()
  while True:
    if time.ticks_ms() - last_tick > 60000:
      last_tick = time.ticks_ms()
      #Get temp/humi from sensor
      stemp = sensor.temperature
      shumi = sensor.relative_humidity
      print("Temperature: %0.2f C" % stemp)
      print("Humidity: %0.2f %%" % shumi)

      #Build JSON payload
      payload = [ {
                  "channel": 1,
                  "value": stemp,
                  "type": "temp",
                  "unit": "c"
                },
                {
                  "channel": 2,
                  "value": shumi,
                  "type": "rel_hum",
                  "unit": "p"
                } ]

      #client.connect()
      mqtt_msg = json.dumps(payload)
      client.publish(mqtt_topic, mqtt_msg)
      #client.disconnect()