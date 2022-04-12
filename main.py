import utime
import json
import network
from umqtt.simple import MQTTClient
from machine import Pin, I2C
import ahtx0
import ssd1306
import senko
import ntp_sync

pub_last_tick = 0
pub_delay_ms = 900000
pub_first_loop = True
ntp_delay_ms = 3600000
ntp_last_tick = 0
ntp_first_loop = True
oc_last_tick = 0
oc_delay_ms = 1000
oc = 0
last_min = 0
MQTT_ACTIVE = False

#Sensor setup
i2c = I2C(scl=Pin(5), sda=Pin(4))
sensor = ahtx0.AHT20(i2c)
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
utime.sleep_ms(20)
oled.rotate(False)
stemp = 0
shumi = 0

#MQTT setup
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

ntp_sync.sync_localtime()

try:
  OTA = senko.Senko(
    user="yannickgagne",
    repo="AmbientBug",
    branch="main",
    files=["main.py"]
  )

  if OTA.update():
    print("Updating from Github...")
    oled.fill(0)
    oled.text("Updating...", 0, 0, 1)
    oled.show()
    time.sleep_ms(2000)
    machine.reset()
except:
  print("Updating failed...")

MQTT_GO = True
#Publish dummy data to Cayenne
if MQTT_GO:
  #client.connect()
  while True:
    if (pub_first_loop) or (utime.ticks_diff(utime.ticks_ms(), pub_last_tick) > pub_delay_ms): #loop 1 time per minute
      MQTT_ACTIVE = True
      pub_first_loop = False
      pub_last_tick = utime.ticks_ms()
      #Check if WIFI is up
      try:
        if st_if.isconnected() == False:
          st_if.connect(ssid, password)
          while st_if.isconnected() == False:
            pass
      except:
        print("WIFI failed...")
      #Get temp/humi from sensor
      try:
        stemp = sensor.temperature
        shumi = sensor.relative_humidity
        print("Temperature: %0.2f C" % stemp)
        print("Humidity: %0.2f %%" % shumi)
      except:
        print("Sensor reading failed...")
      #Build JSON payload
      try:
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
      except:
        print("MQTT publish failed...")
      MQTT_ACTIVE = False

    if not MQTT_ACTIVE:
      #update display when minute changes
      if not last_min == utime.localtime()[4]:
        #OLED
        try:
          now = utime.localtime()
          oled.fill(0)
          oled.text('%0.1f C / %0.1f %%' % (stemp, shumi), 0, 0, 1)
          oled.text('%02d:%02d %02d/%02d/%d' % (now[3], now[4], now[2], now[1], now[0]), 0, 16, 1)
          oled.show()
        except:
          print("OLED update failed...")
        last_min = utime.localtime()[4]

      #update small thingy to show that mcu is alive
      if utime.ticks_diff(utime.ticks_ms(), oc_last_tick) > oc_delay_ms: #loop 1 time per 2 seconds
        try:
          oled.fill_rect(120,0,128,8,0)
          oled.show()
          if oc == 0:
            oled.text("|", 120, 0, 1)
          if oc == 1:
            oled.text("/", 120, 0, 1)
          if oc == 2:
            oled.text("-", 120, 0, 1)
          if oc == 3:
            oled.text("\\", 120, 0, 1)
          oc_last_tick = utime.ticks_ms()
          oled.show()
          oc += 1
          if oc > 3:
            oc = 0
        except:
          print("Active thingy failed...")

      #sync rtc/localtime to internet ntp server
      if utime.ticks_diff(utime.ticks_ms(), ntp_last_tick) > ntp_delay_ms: #loop 1 time per hour
        try:
          ntp_sync.sync_localtime()
          print("Synced time OK")
        except:
          print("NTP sync failed...")
        ntp_last_tick = utime.ticks_ms()
