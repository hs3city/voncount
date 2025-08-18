# SPDX-UrlCopyrightText: 2022-present Claude
#
# SPDX-License-Identifier: MIT
from .process_image import process_image

from .backend.mqtt import MqttBackend

import os
import random

broker = os.getenv("MQTT_BROKER", "mqtt.hs3")
port = 1883

# generate client ID with pub prefix randomly
client_id = f"voncount-mqtt-{random.randint(0, 100)}"
username = os.getenv("MQTT_USER", "")
password = os.getenv("MQTT_PASSWORD", "")


if __name__ == "__main__":
    backend = MqttBackend(process_image, broker, port, username, password)
    backend.run()
