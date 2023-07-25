import serial
from serial import SerialException

# This Python script writes a file containing 'A' (GPS locked) or 'V' (GPS not
# locked) to the path defined in GPS_STATUS_FILE.
#
# Must be run with sudo.

SERIAL_PORT = "/dev/serial0"
GPS_STATUS_FILE = "/tmp/gps-status"
running = True

def write_file(status):
    with open(GPS_STATUS_FILE, 'w') as f:
        f.write(status)

# Reads the data from the serial port and parses NMEA messages.
def getPositionData(gps):
    data = gps.readline()
    message = data[0:6]
    if (message == "$GNRMC".encode()):
        # GNRMC = Recommended minimum specific GPS/Transit data
        # Reading the GPS fix data is an alternative approach that also works
        parts = data.decode("utf-8").split(",")
        if parts[2] == 'V':  # A = data valid | V = data not valid
            # print("GPS acquiring")
            write_file('V')
        else:
            # print("GPS locked")
            write_file('A')
    else:
        # Handle other NMEA messages and unsupported strings
        pass

print("Monitoring for GPS lock!")
write_file('V')
gps = serial.Serial(SERIAL_PORT, baudrate = 9600, timeout = 0.5)

while running:
    try:
        getPositionData(gps)
    except KeyboardInterrupt:
        running = False
        gps.close()
        print("Application closed!")
    except SerialException:
        # print("Serial Exception. Trying to re-connect.")
        # Try re-connecting.
        gps.close()
        gps = serial.Serial(SERIAL_PORT, baudrate = 9600, timeout = 0.5)
