import RPi.GPIO as GPIO
import dht11
import time
import requests
import uuid
MYMAC=hex(uuid.getnode())


# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#GPIO.cleanup()

url2="https://rasserver.up.railway.app/api/send_temp_and_humi/"


# read data using Pin GPIO21 
instance = dht11.DHT11(pin=21)
i=0
while True:
    result = instance.read()
    if result.is_valid():
        if i>20 :
            i=0
            data={}
            data["temperature"]= result.temperature
            data["humidity"]= result.humidity
            data["ip_mac"]=MYMAC
            print(data)
            # js=json.dumps(data)
            result = requests.post(url2,json=data)
        else:
            i+=1
