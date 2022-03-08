import time
import json
import network
from umqtt.simple import MQTTClient
from machine import Pin, I2C
import ahtx0
import ssd1306

pub_last_tick = 0
pub_delay_ms = 60000
oc_last_tick = 0
oc_delay_ms = 2000
oc = 0

#Sensor setup
i2c = I2C(scl=Pin(5), sda=Pin(4))
sensor = ahtx0.AHT20(i2c)
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
time.sleep_ms(20)
oled.rotate(False)

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

st_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)
 
if st_if.isconnected() == True:
  print("Already connected")
 
st_if.active(True)
ap_if.active(False)
st_if.connect(ssid, password)
 
while st_if.isconnected() == False:
  pass
 
print("Connection successful")
print(st_if.ifconfig())

MQTT_GO = True
#Publish dummy data to Cayenne
if MQTT_GO == True:
  #client.connect()
  while True:
    if time.ticks_diff(time.ticks_ms(), oc_last_tick) > oc_delay_ms: #loop 1 time per 2 seconds
      if oc == 0:
        oled.text("|", 120, 0, 1)
      if oc == 1:
        oled.text("/", 120, 0, 1)
      if oc == 2:
        oled.text("-", 120, 0, 1)
      if oc == 3:
        oled.text("\", 120, 0, 1)
      oc_last_tick = time.ticks_ms()
      oled.show()
      oc += 1
      if oc > 3:
        oc = 0
        
    if time.ticks_diff(time.ticks_ms(), pub_last_tick) > pub_delay_ms: #loop 1 time per minute
      pub_last_tick = time.ticks_ms()
      #Get temp/humi from sensor
      stemp = sensor.temperature
      shumi = sensor.relative_humidity
      print("Temperature: %0.2f C" % stemp)
      print("Humidity: %0.2f %%" % shumi)
      #OLED
      oled.fill(0)
      oled.text('%0.2f C' % stemp, 0, 0, 1)
      oled.text('%0.2f %%' % shumi, 0, 16, 1)
      oled.show()
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

      client.connect()
      mqtt_msg = json.dumps(payload)
      client.publish(mqtt_topic, mqtt_msg)
      client.disconnect()
