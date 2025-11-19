import time
import board
import digitalio
import busio
from seeed_sscma import SSCMA

# ---------------------------
# Setup LEDs
# ---------------------------
red_led = digitalio.DigitalInOut(board.D2)
red_led.direction = digitalio.Direction.OUTPUT

green_led = digitalio.DigitalInOut(board.D3)
green_led.direction = digitalio.Direction.OUTPUT

red_led.value = False
green_led.value = False

# ---------------------------
# Setup I2C + Vision AI
# ---------------------------
i2c = busio.I2C(board.SCL, board.SDA)
ai = SSCMA(i2c)

# Wait until module is ready
while not ai.begin():
    print("Vision is NOT READY!")
    time.sleep(1)

print("Vision is Ready.")

# ---------------------------
# Main loop
# ---------------------------
while True:
    result = ai.invoke(single=1, filter=False, getimg=False)

    class1_seen = False
    class2_seen = False

    if result == 0:
        boxes = ai.boxes()

        if len(boxes) == 0:
            # No objects → LEDs OFF
            red_led.value = False
            green_led.value = False
            print("No objects → LEDs OFF")

        # Examine all detections
        for box in boxes:
            cid = box.target
            score = box.score

            if score > 0.4:
                if cid == 1:
                    class1_seen = True
                elif cid == 2:
                    class2_seen = True

        # Priority: CLASS 1 → CLASS 2 → NONE
        if class1_seen:
            print("Class 1 detected → RED ON, GREEN OFF")
            red_led.value = True
            green_led.value = False

        elif class2_seen:
            print("Class 2 detected → GREEN ON, RED OFF")
            green_led.value = True
            red_led.value = False

        else:
            print("No valid detection → LEDs OFF")
            red_led.value = False
            green_led.value = False

    else:
        print("Error running model → LEDs OFF")
        red_led.value = False
        green_led.value = False

    time.sleep(0.1)
