import time
import sys

from picamera2 import Picamera2
import numpy as np
import torch
from gpiozero import LEDCharDisplay

display = LEDCharDisplay(3, 2, 22, 10, 9, 4, 17, active_high=False) # 27 is dot
#declared the GPIO pins for (a,b,c,d,e,f,g) and declared its CAS

model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or yolov5n - yolov5x6, custom

picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start()

while True:
    img = picam2.capture_array()

    print(img.shape)

    # Inference
    results = model(img)
    results.print()

    classes = np.array(results.xyxy[0][:, -1])
    count_by_name = {name: np.sum(classes == nr) for nr, name in results.names.items()}

    print("persons:", count_by_name["person"], "pizzas: ", count_by_name["pizza"])

    persons = min(count_by_name["person"], 15)
    char = f"{persons:X}"[-1]
    print("Showing on display: ", char)
    display.value = char

    time.sleep(10)
