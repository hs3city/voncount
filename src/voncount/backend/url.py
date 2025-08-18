# SPDX-FileCopyrightText: 2022-present Claude
#
# SPDX-License-Identifier: MIT
import numpy as np
import cv2
import urllib
import time

from .ibackend import IBackend

SLEEP_SECONDS_BETWEEN_DETECTS = 60


class UrlBackend(IBackend):
    def __init__(self, process_image_function, url):
        self.process_image = process_image_function
        self.url = url

    def publish_results(self, counts, lux):
        print(counts)

    def process_file(self):
        req = urllib.request.urlopen(self.url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        lux = 100

        return img, lux

    def run(self):
        while True:
            img, lux = self.process_file()

            counts = self.process_image(img, lux)

            self.publish_results(counts, lux)

            time.sleep(SLEEP_SECONDS_BETWEEN_DETECTS)
