# LTX 2023 Time Card mini timer

For LTX 2023, I built a timing platform centered around Timebeat's [Timecard mini](https://store.timebeat.app/products/ocp-tap-timecard-mini-complete-edition).

![Time Card mini with timer stuff](/images/time-card-mini-timer.jpg)

The time card's GPS modem is used to acquire the precise time using GPS or GNSS satellites, and that time is then displayed on a tiny 1.3" TFT connected through the Raspberry Pi GPIO pins.

A Blinkstick Nano shows different colors and patterns depending on what time it is. It will help me split up time during a live stream into 5 minute segments, so Chris (from Crosstalk Solutions) and I can keep the stream moving along during the busy day at [LTX 2023](https://www.ltxexpo.com), raising money for the [ITDRC](https://www.itdrc.org).

## U-blox GPS/GNSS module Timebeat setup

Timebeat maintains their own software that integrates PPS output from the U-blox GPS/GNSS module into PTP/PPS inputs and outputs on the Raspberry Pi CM4. The `timebeat` service is configured via `/etc/timebeat/timebeat.yml`, and to make sure time is served up through GPS _only_, you will need to edit that file.

  1. Edit the timebeat config file: `/etc/timebeat/timebeat.yml`
  1. Comment out the `pps` input config example on interface `eth0` in the `primary_clocks` section.
  1. Copy the `timecard-mini` protocol item into the top of the `primary_clocks` section.
  1. Restart the timebeat service: `sudo systemctl restart timebeat`

### Using `gpsd` instead (optional, not recommended)

If you want to use `gpsd` instead:

  1. Stop and disable the `timebeat` service: `sudo systemctl stop timebeat && sudo systemctl disable timebeat`
  1. Make sure `console=serial0,115200` is _not_ inside the file `/boot/cmdline.txt` (if so, delete that portion, which sets up `ttyS0`/`serial0` as a UART, then reboot the Pi before proceeding).
  1. Install `gpsd`: `sudo apt install -y gpsd`
  1. Edit the `gpsd` config file: `sudo nano /etc/default/gpsd`
  1. Change the `DEVICES` line to: `DEVICES="/dev/ttyS0"` and save (Ctrl + O, Ctrl + X)
  1. Restart the `gpsd` service: `sudo systemctl restart gpsd`
  1. Run `gpsmon` to make sure the GPS module is found—it should show up in the `DEVICES` output, and after a while, once GPS satellites are found, you should see TODO.

Once `gpsd` is running and configured, you need to set the system to use the GPS module as a time source. The GPS module needs to output PPS (Pulse Per Second) for this to work, and luckily, the U-blox _should_. However, it _won't_ until the receiver gets a GPS fix (and this can take a while sometimes, especially if you don't have a clear view of the sky).

You can stop `gpsd` and run `ppscheck /dev/ttyS0` to monitor for PPS's, or just wait (and use `gpsmon` while `gpsd` is running—it should also show PPS's).

Setting up NTP or Chrony to use `gpsd` for PPS input is not covered here. I'll do that at some point in the future.

## Blinkstick Nano setup

For quick visual indication of how much time remains in 5-minute segments during an LTX livestream, I have a [Blinkstick Nano](https://www.blinkstick.com/products/blinkstick-nano) plugged into the USB-A port on the Timecard mini.

### Timecard Mini USB controller setup

(Note: I used a [PiTray mini](https://sourcekit.cc/#/) for the eeprom flashing. Procedures to program the CM4 eeprom using usbboot vary by CM4 IO board model, but typically you would disable the eMMC Boot option, whether via dip switch or jumper.)

  1. Plug the CM4 into a PiTray mini.
  1. Ensure the eMMC Boot switch is 'OFF'
  1. Plug the PiTray mini into your computer.
  1. Follow [these steps](https://www.jeffgeerling.com/blog/2022/how-update-raspberry-pi-compute-module-4-bootloader-eeprom) to flash the eeprom of the CM4 using `usbboot`.
  1. When it comes time to edit the `boot.conf` file, add the following line to the end of the file, and save it, before running `./update-pieeprom.sh`.
  1. After the update is complete, unplug the CM4 and plug it back into the Timecard mini.

### Blinkstick Nano setup

The Pypi `blickstick` package has a few bugs currently, but you will still use it for the Python script that will display time on the LED.

  1. Install `pyusb`: `sudo pip3 install pyusb`
  1. Install `blinkstick`: `sudo pip3 install blinkstick`
  1. Copy the `blinkstick/` directory into `/opt`
  1. Create a systemd unit for `blinktime.py`: `sudo nano /lib/systemd/system/blinktime.service`
  3. Inside, put:

     ```
     [Unit]
     Description=blinktime
     Wants=network.target
     After=network.target
      
     [Service]
     Type=simple
     ExecStart=/usr/bin/python3 blinktime.py
     WorkingDirectory=/opt/blinkstick
     Restart=always
      
     [Install]
     WantedBy=multi-user.target
     ```

  4. Reload systemctl: `sudo systemctl daemon-reload`
  5. Enable the service: `sudo systemctl enable blinktime.service`
  6. Start the service: `sudo systemctl start blinktime`

## Adafruit mini PiTFT 1.3 HAT setup

If you connect an [Adafruit mini PiTFT HAT](https://www.adafruit.com/product/4484) to the Rasbperry Pi GPIO header, you can display the current time and GPS status on a handy little screen.

Hardware-wise, to clear the sandwich stack of all the Time Card boards, I had to purchase a [GPIO stacking female header kit](https://amzn.to/44YZ5VC).

For software setup, you need to copy over the `wopr` code, then set it to run on boot. And yes, `wopr` is a reference to the game countdown display on the [War Games](https://en.wikipedia.org/wiki/WarGames) WOPR computer.

### Adafruit Prerequisites

```
sudo apt install -y python3-pip fonts-dejavu python3-pil python3-numpy
sudo pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo python3 raspi-blinka.py
```

Reboot, then:

```
sudo pip3 install adafruit-circuitpython-rgb-display
sudo pip3 install --upgrade --force-reinstall spidev
```

### GPS setup

This script was tested along with Timebeat's [Multi-constellation GPS / GNSS module](https://store.timebeat.app/products/gnss-raspberry-pi-cm4-module?variant=42280855699627), specifically the U-blox LEA-M8F variant.

There is a script that checks on the GPS status and writes to a file in `/tmp/gps-status` either 'A' (GPS is locked) or 'V' (GPS is not locked / acquiring).

This script is used by the WOPR script to display GPS status information.

  1. Copy the `gps/` directory into `/opt` on the Raspberry Pi.
  1. Create a systemd unit for `gpslock-timebeat.py`: `sudo nano /lib/systemd/system/gpslock.service`
  3. Inside, put:

     ```
     [Unit]
     Description=gpslock
     Wants=network.target
     After=network.target
      
     [Service]
     Type=simple
     ExecStart=/usr/bin/python3 gpslock-timebeat.py
     WorkingDirectory=/opt/gps
     Restart=always
      
     [Install]
     WantedBy=multi-user.target
     ```

  4. Reload systemctl: `sudo systemctl daemon-reload`
  5. Enable the service: `sudo systemctl enable gpslock.service`
  6. Start the service: `sudo systemctl start gpslock`

If you are not running Timebeat, you can directly access the serial port to get GPS data using the `gpslock.py` script—just copy that script into the `/opt/gps` folder, and update the `ExecStart` statement to point to it.

### WOPR setup

  1. Copy the `wopr/` directory into `/opt` on the Rasbperry Pi.
  2. Create a systemd unit for `wopr.py`: `sudo nano /lib/systemd/system/wopr.service`
  3. Inside, put:

     ```
     [Unit]
     Description=WOPR
     Wants=network.target
     After=network.target
      
     [Service]
     Type=simple
     ExecStart=/usr/bin/python3 wopr.py
     WorkingDirectory=/opt/wopr
     Restart=always
      
     [Install]
     WantedBy=multi-user.target
     ```

  4. Reload systemctl: `sudo systemctl daemon-reload`
  5. Enable the service: `sudo systemctl enable wopr.service`
  6. Start the service: `sudo systemctl start wopr`

## License

MIT

## Author

This project was built in 2023 for LTX Expo by [Jeff Geerling](https://www.jeffgeerling.com).
