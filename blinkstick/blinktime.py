#!/usr/bin/env python3

import time
import sys
import signal
from datetime import datetime

try:
    from blinkstick import blinkstick
except ImportError:
    print("Blinkstick library not present. Run 'pip install blinkstick'")

global blinkstick_state
blinkstick_state = 'green'
run = True


# Set the current color state based on 5 minute intervals.
def set_current_state():
    current_time = datetime.now()
    hour = current_time.strftime('%H')
    minute = current_time.strftime('%M')
    second = current_time.strftime('%S')

    debug_time = hour + ':' + minute + ':' + second

    # Green pulse during first 3 minutes.
    if minute[-1] in ['0', '1', '2', '5', '6', '7']:
        current_state = 'green'
        # print(debug_time + ' - green')
    # Amber pulse during 4th minute.
    elif minute[-1] in ['3', '8']:
        current_state = 'amber'
        # print(debug_time + ' - amber')
    # Red colors during 5th minute.
    else:
        if int(second) < 30:
            current_state = 'orange'
            # print(debug_time + ' - orange')
        elif 30 <= int(second) < 50:
            current_state = 'red'
            # print(debug_time + ' - red')
        else:
            current_state = 'flash'
            # print(debug_time + ' - flash')

    # Update blinkstick state if it should change.
    if current_state != blinkstick_state:
        print(debug_time + ' - Setting state to: ' + current_state)
        update_blinkstick_state(current_state)


# Update the state of the blinkstick.
def update_blinkstick_state(new_state):
    global blinkstick_state
    # print('Setting state to: ' + new_state)

    for bstick in blinkstick.find_all():
        bstick.set_random_color()
        if new_state == 'green':
            bstick.morph(red=0, green=255, blue=0, duration=500)
        elif new_state == 'amber':
            bstick.morph(red=255, green=191, blue=0, duration=500)
        elif new_state == 'orange':
            bstick.morph(red=254, green=75, blue=3, duration=500)
        elif new_state == 'red':
            bstick.morph(red=255, green=0, blue=0, duration=500)
        elif new_state == 'flash':
            bstick.blink(red=255, green=0, blue=0, repeats=11, delay=500)
        elif new_state == 'off':
            bstick.turn_off()

    blinkstick_state = new_state


def handler_stop_signals(signum, frame):
    global run
    run = False
    update_blinkstick_state('off')
    sys.exit()


# Handle termination signals.
signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)


start_time = time.time()
interval = 1
try:
    # Initialize the blinkstick.
    update_blinkstick_state(blinkstick_state)

    # Loop forever, every second.
    while True:
        set_current_state()
        time.sleep(start_time + interval * 1 - time.time())
        interval += 1
except KeyboardInterrupt:
    print("Quitting")
    update_blinkstick_state('off')
    sys.exit()
