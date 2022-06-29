import RPi.GPIO as GPIO
import uuid
import audio_control as ac
from paho.mqtt import client as mqtt_client
import json
import requests
from base64 import b64encode

MYMAC=hex(uuid.getnode())

broker = 'broker.emqx.io'
port = 1883
topicListen = "dutras/"+MYMAC
topicRequest="dutras/server"
# generate client ID with pub prefix randomly
client_id = "ras-ngo-van-dong"
username = 'aaa'
password = 'bbb'


a_controller = ac.AudioControl()

#global var
control_mode = False

LED=24
# BT=23
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(LED, GPIO.OUT)  #LED to GPIO24
# GPIO.setup(BT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(BT, GPIO.IN)


url="https://rasserver.up.railway.app/api/ras_predict/"


in1 = 2
in2 = 3
en = 4


GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
p=GPIO.PWM(en,1000)

p.start(25)
GPIO.output(in2,GPIO.LOW)


def switchDC(cmd):
    if cmd:
        GPIO.output(in1,GPIO.HIGH)
    else:
        GPIO.output(in1,GPIO.LOW)


def sendWav():
    f=open("temp.wav","rb")
    enc=b64encode(f.read())
    f.close()
    data={}
    data["fileCode"]=enc.decode("utf-8")
    data["ipMac"]=MYMAC
    # js=json.dumps(data)
    # print(type(js))
    result = requests.post(url,json=data)

    

def switch_record(channel):
    global control_mode
    global client
    if control_mode:
        print("Stop record")
        control_mode = False
        a_controller.stop_recording()
        print('processing...')
        sendWav()
    else:
        print("Start record")
        control_mode = True
        a_controller.start_recording(ac.DEFAULT_SAVE_FILENAME)

# GPIO.add_event_detect(BT, GPIO.FALLING, callback=switch_record, bouncetime=1000)


def execute(cmd,gate):
    if gate==1:
        if cmd==0:
            GPIO.output(LED, False)
        if cmd==1:
            GPIO.output(LED, True)
        if cmd==-1:
            print("Unknown!")
    if gate==2:
        switchDC(cmd)

def request(cmd):
    pass

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, req):
        # execute(req["command"])
        js=json.loads(req.payload.decode())
        execute(js['command'],js['gate'])
        print(js)
    client.subscribe(topicListen)
    client.on_message = on_message



if __name__ == '__main__':
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()
