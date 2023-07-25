#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# Modified for LTX2023 by Jeff Geerling.

# -*- coding: utf-8 -*-

import time
import subprocess
import digitalio
import board
import signal
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789


# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=240,
    height=240,
    x_offset=0,
    y_offset=80,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 180

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("wopr-tweaked/wopr-tweaked.ttf", 32)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

run = True
GPS_STATUS_FILE = "/tmp/gps-status"


def clear_image():
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)


def draw_lines(line1='', line2='', line3='', line4='', line5='', line6='', line7='', line8=''):
    # Write lines of text.
    y = top + 4
    draw.text((x, y), line1, font=font, fill="#FFFFFF")
    y += font.getsize(line1)[1] + 6
    draw.text((x, y), line2, font=font, fill="#FFFFFF")
    y += font.getsize(line2)[1] + 6
    draw.text((x, y), line3, font=font, fill="#FFFFFF")
    y += font.getsize(line3)[1] + 6
    draw.text((x, y), line4, font=font, fill="#FFFFFF")
    y += font.getsize(line4)[1] + 6
    draw.text((x, y), line5, font=font, fill="#FFFFFF")
    y += font.getsize(line5)[1] + 6
    draw.text((x, y), line6, font=font, fill="#FFFFFF")
    y += font.getsize(line6)[1] + 6
    draw.text((x, y), line7, font=font, fill="#FFFFFF")
    y += font.getsize(line7)[1] + 6
    draw.text((x, y), line8, font=font, fill="#FFFFFF")

    # Display image.
    disp.image(image, rotation)


def handler_stop_signals(signum, frame):
    global run
    run = False
    clear_image()
    line1 = '|-------------|'
    line2 = '|             |'
    line3 = '|    WOPR     |'
    line4 = '|   SERVICE   |'
    line5 = '|   STOPPED   |'
    line6 = '|             |'
    line7 = '|             |'
    line8 = '|-------------|'
    draw_lines(line1, line2, line3, line4, line5, line6, line7, line8)
    sys.exit()


# Handle termination signals.
signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

# Initial greetings display.
clear_image()
line1 = '|-------------|'
line2 = '|  GREETINGS  |'
line3 = '|   LTX2023   |'
line4 = '|             |'
line5 = '|             |'
line6 = '|             |'
line7 = '|             |'
line8 = '|-------------|'
draw_lines(line1, line2, line3, line4, line5, line6, line7, line8)
time.sleep(3)

# Main loop.
while run:
    clear_image()

    dt = datetime.now()
    Time = '{:%H:%M:%S}.{:02.0f}'.format(dt, dt.microsecond / 10000.0)
    with open(GPS_STATUS_FILE) as f: gps_status = f.read()
    GPS = "LOCKED" if gps_status == "A" else "-     "

    line1 = '|-------------|'
    line2 = '|    TIME:    |'
    line3 = '| ' + Time + ' |'
    line4 = '|-------------|'
    line5 = '|             |'
    line6 = '| GPS: ' + GPS + ' |'
    line7 = '|             |'
    line8 = '|-------------|'
    draw_lines(line1, line2, line3, line4, line5, line6, line7, line8)

    # Display image.
    time.sleep(0.05)
