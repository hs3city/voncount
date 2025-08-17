# SPDX-UrlCopyrightText: 2022-present Claude
#
# SPDX-License-Identifier: MIT

import time
import sys

import numpy as np
from ultralytics import YOLO

from .backend.url import UrlBackend

CONFIDENCE_CUTOFF = 0.4
MIN_LUX_LEVEL = 5  # if it's too dark, don't count people, save energy

counts = None
lux = 0
newimage = None

model = YOLO("yolo11m.pt")


def process_image(img, lux):
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
        _ = results.plot()

        print("persons:", count_by_name["person"], "pizzas: ", count_by_name["pizza"])
        sys.stdout.flush()

    counts = {
        "persons": int(count_by_name["person"]),
        "pizzas": int(count_by_name["pizza"]),
    }

    return counts


if __name__ == "__main__":
    url = "https://ultralytics.com/images/bus.jpg"
    backend = UrlBackend(process_image, url)
    backend.run()
