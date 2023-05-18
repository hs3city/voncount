import os
import sys
import socket
import threading
import time
import json
import random

from picamera2 import Picamera2
import numpy as np
import torch
import cv2
from gpiozero import LEDCharDisplay
from paho.mqtt import client as mqtt_client


counts = None
lux = None
newimage = None


broker = os.getenv('MQTT_BROKER', 'mqtt.local')
port = 1883
topic_people = "sensor/space/member/present"
topic_lux = "sensor/light/room/0"

# generate client ID with pub prefix randomly
client_id = f'voncount-mqtt-{random.randint(0, 100)}'
username = os.getenv('MQTT_USER', '')
password = os.getenv('MQTT_PASSWORD', '')


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


def publish(client):
    people = counts["persons"]
    result = client.publish(topic_people, people)
    result = client.publish(topic_lux, lux)
    status = result[0]
    if status == 0:
        print(f"Send `{people}` (lux `{lux}`) to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def server_count():
    PORT=26178
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", PORT))
        sock.listen()
        print("listening")
        while True:
            conn, addr = sock.accept()
            print("shared")
            conn.send(json.dumps(counts).encode("UTF-8"))
            conn.close()

def serve_img(conn):
    try: 
        print("img shared")
        if newimage is None:
            conn.close()
        is_success, buffer = cv2.imencode(".png", newimage)
        conn.send(buffer)
    finally:
        conn.close()

def server_img():
    PORT=26179
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", PORT))
        sock.listen()
        print("listening")
        while True:
            conn, addr = sock.accept()
            threading.Thread(target=serve_img, args=(conn,)).start()

threading.Thread(target=server_count, daemon=True).start()
threading.Thread(target=server_img, daemon=True).start()

MIN_LUX_LEVEL = 25  # if it's too dark, we're not going to count people, to save energy

display = LEDCharDisplay(3, 2, 22, 10, 9, 4, 17, dp=27, active_high=False) # 27 is dot
#declared the GPIO pins for (a,b,c,d,e,f,g) and declared its CAS
display.value = " ."  # signal for startup

model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or yolov5n - yolov5x6, custom

picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start()

client = connect_mqtt()
client.loop_start()

prevchar = "NOT_A_CHAR"
while True:
    img = picam2.capture_array()
    metadata = picam2.capture_metadata()
    lux = metadata["Lux"]
    if lux < MIN_LUX_LEVEL:
        print(f"Too dark (lux={lux:.2f}), not counting people")
        sys.stdout.flush()
        count_by_name = {"person": 0, "pizza": 0}
    else:
        print(f"Bright enough (lux={lux:.2f}), yoloing now")
        img = img[600:, 200:-600, :]
        print(img.shape)
        sys.stdout.flush()

        # Inference
        results = model(img)
        results.print()

        scores = results.xyxy[0][:, -2]
        classes = np.array(results.xyxy[0][scores > .4, -1])
        count_by_name = {name: np.sum(classes == nr) for nr, name in results.names.items()}
        newimage = results.render()[0]

        print("persons:", count_by_name["person"], "pizzas: ", count_by_name["pizza"])
        sys.stdout.flush()

    persons = min(count_by_name["person"], 15)
    char = f"{persons:X}"[-1]
    if count_by_name["pizza"]:
        char += "."
    if char == "0" and prevchar in "0 ":
        print(f"Multiple 0's in a row, switching off display")
        sys.stdout.flush()

        char = " "
    print(f"Showing on display: {repr(char)}")
    sys.stdout.flush()
    display.value = char
    prevchar = char
    counts = {"persons": int(count_by_name["person"]), "pizzas": int(count_by_name["pizza"])}

    publish(client)

    time.sleep(10)
