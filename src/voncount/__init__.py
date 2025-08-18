# SPDX-UrlCopyrightText: 2022-present Claude
#
# SPDX-License-Identifier: MIT
from .backend.file import FileBackend
from .backend.url import UrlBackend
from .backend.mqtt import MqttBackend
from .process_image import process_image as process_image

topic_people = "sensor/space/member/present"
topic_lux = "sensor/light/room/0"

__all__ = ["FileBackend", "UrlBackend", "MqttBackend", "process_image"]
