import os
import sys
import socket
import threading
import time
import json
import random
import urllib
import numpy as np
from ultralytics import YOLO
import cv2

NO_RPI = len(sys.argv) == 2 and sys.argv[1] == "NO_RPI"

if NO_RPI:
    print("Running in no-rpi mode")
else:
    from picamera2 import Picamera2
    from gpiozero import LEDCharDisplay
    from paho.mqtt import client as mqtt_client


CONFIDENCE_CUTOFF = 0.4
MIN_LUX_LEVEL = 5  # if it's too dark, don't count people, save energy

SLEEP_SECONDS_BETWEEN_DETECTS = 60
broker = os.getenv('MQTT_BROKER', 'mqtt.hs3')
port = 1883
topic_people = "sensor/space/member/present"
topic_lux = "sensor/light/room/0"

# generate client ID with pub prefix randomly
client_id = f'voncount-mqtt-{random.randint(0, 100)}'
username = os.getenv('MQTT_USER', '')
password = os.getenv('MQTT_PASSWORD', '')

counts = None
lux = None
newimage = None


def connect_mqtt() -> "mqtt_client":
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
    data = (counts["persons"], lux)
    topics = (topic_people, topic_lux)
    for (datum, topic) in zip(data, topics):
        result = client.publish(topic, datum)
        status = result[0]
        if status == 0:
            print(f"Send `{datum}` to topic `{topic}`")
        else:
            print(f"Failed to send message `{datum}` to topic {topic}")


def server_count():
    PORT = 26178
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
    PORT = 26179
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

if not NO_RPI:
    display = LEDCharDisplay(3, 2, 22, 10, 9, 4, 17, dp=27,
                             active_high=False)  # 27 is dot
    # declared the GPIO pins for (a,b,c,d,e,f,g) and declared its CAS
    display.value = " ."  # signal for startup
model = YOLO("yolo11n.pt")

if not NO_RPI:
    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start()

    client = connect_mqtt()
    client.loop_start()

prevchar = "NOT_A_CHAR"
while True:
    if NO_RPI:
        req = urllib.request.urlopen('https://ultralytics.com/images/bus.jpg')
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        lux = 100
    else:
        img = picam2.capture_array()
        metadata = picam2.capture_metadata()
        lux = metadata["Lux"]
    if lux < MIN_LUX_LEVEL:
        print(f"Too dark (lux={lux:.2f}), not counting people")
        sys.stdout.flush()
        count_by_name = {"person": 0, "pizza": 0}
    else:
        print(f"Bright enough (lux={lux:.2f}), yoloing now")
        print(img.shape)
        sys.stdout.flush()

        # Inference
        infer_start = time.time()
        results = model([img])[0]
        infer_run_sec = time.time() - infer_start
        print(f"Inference took {infer_run_sec:.03f} seconds")

        scores = results.boxes.conf
        classes = np.array(results.boxes.cls)[scores > CONFIDENCE_CUTOFF]
        print(scores)
        print(classes)
        count_by_name = {
            name: np.sum(classes == nr) for nr, name in results.names.items()
        }
        newimage = results.plot()

        print("persons:", count_by_name["person"], "pizzas: ",
              count_by_name["pizza"])
        sys.stdout.flush()

    persons = min(count_by_name["person"], 15)
    char = f"{persons:X}"[-1]
    if count_by_name["pizza"]:
        char += "."
    if char == "0" and prevchar in "0 ":
        print("Multiple 0's in a row, switching off display")
        sys.stdout.flush()

        char = " "
    print(f"Showing on display: {repr(char)}")
    sys.stdout.flush()
    if not NO_RPI:
        display.value = char
    prevchar = char
    counts = {"persons": int(count_by_name["person"]),
              "pizzas": int(count_by_name["pizza"])}

    if not NO_RPI:
        publish(client)

    time.sleep(SLEEP_SECONDS_BETWEEN_DETECTS)
