# SPDX-UrlCopyrightText: 2022-present Claude
#
# SPDX-License-Identifier: MIT

import asyncio
import os
import sys
import random

# FIXME: Oh the nasty things we do for our tests to pass!
try:
    from picamera2 import Picamera2
    from gpiozero import LEDCharDisplay
except ImportError:
    pass
from paho.mqtt import client as mqtt_client
from base64 import b64encode


SLEEP_SECONDS_BETWEEN_DETECTS = 60

broker = os.getenv("MQTT_BROKER", "mqtt.hs3")
port = 1883
topic_people = "sensor/space/member/present"
topic_lux = "sensor/light/room/0"
topic_img = "sensor/space/state_img"

# generate client ID with pub prefix randomly
client_id = f"voncount-mqtt-{random.randint(0, 100)}"
username = os.getenv("MQTT_USER", "")
password = os.getenv("MQTT_PASSWORD", "")

counts = {"persons": 0, "lux": 0}

display = None
newimage = None


def connect_mqtt():
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
            except OSError:
                pass

    client = mqtt_client.Client(client_id=client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker, port)

    def subscribe():
        def on_message(client, userdata, msg):
            payload = int(msg.payload.decode(), 10)
            print(f"Received `{payload}` from `{msg.topic}` topic")

            update_display(payload)

        client.subscribe(topic_people)
        client.on_message = on_message
        print(f"Subscribed to {topic_img}")

    subscribe()

    return client


def publish(client, img, lux):
    payload = {"image": str(b64encode(img).decode("ascii")), "lux": lux}

    topic = topic_img

    result = client.publish(topic, payload)
    status = result[0]

    if status == 0:
        print(f"Sent `{payload}` to topic `{topic}`")
    else:
        print(f"Failed to send message `{payload}` to topic {topic}")


prevchar = "NOT_A_CHAR"


def update_display(persons, pizzas=0):
    global display, prevchar

    persons = min(persons, 15)
    char = f"{persons:X}"[-1]

    if pizzas >= 1:
        char += "."

    if char == "0" and prevchar in "0 ":
        print("Multiple 0's in a row, switching off display")
        sys.stdout.flush()

        char = " "

    print(f"Showing on display: {repr(char)}")
    sys.stdout.flush()

    display.value = char
    prevchar = char


def init_display():
    display = LEDCharDisplay(
        3, 2, 22, 10, 9, 4, 17, dp=27, active_high=False
    )  # 27 is dot
    # declared the GPIO pins for (a,b,c,d,e,f,g) and declared its CAS
    display.value = " ."  # signal for startup

    return display


async def main():
    global display

    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start()

    client = connect_mqtt()
    client.loop_start()

    display = init_display()

    while True:
        img = picam2.capture_array()
        metadata = picam2.capture_metadata()
        lux = metadata["Lux"]

        print(img.shape)
        sys.stdout.flush()

        publish(client, img, lux)

        await asyncio.sleep(SLEEP_SECONDS_BETWEEN_DETECTS)


if __name__ == "__main__":
    asyncio.run(main())
