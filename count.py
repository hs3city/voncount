import sys
import time

from picamera2 import Picamera2
import numpy as np
import torch
from gpiozero import LEDCharDisplay

MIN_LUX_LEVEL = 25  # if it's too dark, we're not going to count people, to save energy

display = LEDCharDisplay(3, 2, 22, 10, 9, 4, 17, dp=27, active_high=False) # 27 is dot
#declared the GPIO pins for (a,b,c,d,e,f,g) and declared its CAS
display.value = " ."  # signal for startup

model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or yolov5n - yolov5x6, custom

picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start()

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
        print(img.shape)
        sys.stdout.flush()

        # Inference
        results = model(img)
        results.print()

        classes = np.array(results.xyxy[0][:, -1])
        count_by_name = {name: np.sum(classes == nr) for nr, name in results.names.items()}

        sys.stdout.flush()
        print("persons:", count_by_name["person"], "pizzas: ", count_by_name["pizza"])

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

    time.sleep(10)
