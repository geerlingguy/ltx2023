import systemd.journal
import socket
import time

GPS_STATUS_FILE = "/tmp/gps-status"

def write_file(status):
    with open(GPS_STATUS_FILE, 'w') as f:
        f.write(status)

def main():
    j = systemd.journal.Reader()
    j.seek_tail()
    j.get_previous()

    # On startup, write out 'V' for acquiring.
    write_file('V')

    # Watch for timebeat log entries to be written.
    while True:
        event = j.wait(-1)
        if event == systemd.journal.APPEND:
            for entry in j:
                if entry['SYSLOG_IDENTIFIER'] == 'timebeat':
                    message = entry['MESSAGE']

                    # Only act on 'adj' entries.
                    if message[0] == 'a':
                        message_parts = message.split(",")
                        delta = message_parts[2]

                        # If the time adjustment is in the ms range or lower,
                        # then GPS signal must be locked (probably lol).
                        if any(x in delta for x in ('ms', 'µs')):
                            write_file('A')
                        else:
                            write_file('V')

if __name__ == '__main__':
    main()
