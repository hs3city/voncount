# SPDX-FileCopyrightText: 2022-present Claude
#
# SPDX-License-Identifier: MIT
import pytest
from pytest_mqtt.model import MqttMessage


import numpy as np
import json
import os
import time
from base64 import b64encode

import voncount

capmqtt_decode_utf8 = True


@pytest.mark.capmqtt_decode_utf8
def test_mqtt_send_receive(mosquitto, capmqtt):
    """
    Check if the backend correctly processes test image and publishes to appropriate topics

    By using the `capmqtt_decode_utf8` marker, the message payloads
    will be recorded as `str`, after decoding them from `utf-8`.
    Otherwise, message payloads would be recorded as `bytes`.
    """

    test_filename = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "assets/pizza_party.jpg"
    )

    arr = np.fromfile(
        test_filename,
        dtype=np.uint8,
    )

    lux = 1337

    with open(f"{test_filename}.json") as f:
        metadata = json.load(f)

    payload = {"image": b64encode(arr).decode("ascii"), "lux": lux}

    backend = voncount.MqttBackend(voncount.process_image, "localhost")

    backend.run_async()

    # FIXME: There **has** to be a better way
    # We are waiting here for the backend startup
    time.sleep(2)

    capmqtt.publish(topic=backend.topic_img, payload=json.dumps(payload))

    # FIXME: same as above
    # Here, we wait for backend to publish the calculated results
    time.sleep(2)

    assert (
        MqttMessage(
            topic=backend.topic_people, payload=str(metadata["persons"]), userdata=None
        )
        in capmqtt.messages
    )
    assert (
        MqttMessage(topic=backend.topic_lux, payload=str(lux), userdata=None)
        in capmqtt.messages
    )

    backend.stop()
