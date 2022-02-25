import time
import json
import network
from umqtt.simple import MQTTClient
from machine import Pin, I2C
import ahtx0

last_tick = time.ticks_ms()
pub_delay_ms = 60000

#Sensor setup
i2c = I2C(scl=Pin(5), sda=Pin(4))
sensor = ahtx0.AHT20(i2c)
time.sleep_ms(20)

#MQTT Cayenne setup
mqtt_user = "qs8$6meFa%D^1Gzw1o9^S5i4plYhPB$q"
mqtt_pass = "d%EYyEkYQCeRw3l3bti6I^%XRbeuV7g8"
mqtt_client_id = "mp001"
mqtt_server = "10.10.1.68"
mqtt_port = 1883
mqtt_room = "cuisine"
mqtt_topic = b"5702/" + mqtt_room + "/" + mqtt_client_id
client = MQTTClient(mqtt_client_id, mqtt_server, port=mqtt_port, user=mqtt_user, password=mqtt_pass, keepalive=60)

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
    if time.ticks_diff(time.ticks_ms(), last_tick) > pub_delay_ms:
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