# SPDX-FileCopyrightText: 2022-present Claude
#
# SPDX-License-Identifier: MIT
import numpy as np
import cv2
import json
import random
from paho.mqtt import client as mqtt_client
from base64 import b64decode

from .ibackend import IBackend

SLEEP_SECONDS_BETWEEN_DETECTS = 60


class MqttBackend(IBackend):
    client_id = f"voncount-mqtt-count-{random.randint(0, 100)}"

    topic_people = "sensor/space/member/present"
    topic_lux = "sensor/light/room/0"
    topic_img = "sensor/space/state_img"

    def __init__(
        self, process_image_function, broker, port=1883, username="", password=""
    ):
        self.process_image = process_image_function
        self.broker = broker
        self.port = port

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        def on_disconnect(client, userdata, rc):
            if rc != 0:
                print("Unexpected MQTT disconnection. Attempting to reconnect.")
                try:
                    client.reconnect()
                except OSError as e:
                    print("Socket error:", e)

        self.client = mqtt_client.Client(client_id=self.client_id)
        self.client.username_pw_set(username, password)
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect

    def publish_results(self, counts, lux):
        data = (counts["persons"], lux)
        topics = (self.topic_people, self.topic_lux)
        for datum, topic in zip(data, topics):
            result = self.client.publish(topic, datum)
            status = result[0]
            if status == 0:
                print(f"Send `{datum}` to topic `{topic}`")
            else:
                print(f"Failed to send message `{datum}` to topic {topic}")

    def subscribe(self):
        def on_message(client, userdata, msg):
            json_payload = msg.payload.decode()
            print(f"Received `{json_payload}` from `{msg.topic}` topic")

            payload = json.loads(json_payload)
            image = b64decode(payload["image"])
            image_np = np.frombuffer(image, dtype=np.uint8)
            image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            lux = payload["lux"]

            counts = self.process_image(image, lux)

            self.publish_results(counts, lux)

        self.client.subscribe(self.topic_img)
        self.client.on_message = on_message
        print(f"Subscribed to {self.topic_img}")

    def run(self):
        self.client.connect(self.broker, self.port)
        self.subscribe()
        self.client.loop_forever()

    def run_async(self):
        self.client.connect(self.broker, self.port)
        self.subscribe()
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
