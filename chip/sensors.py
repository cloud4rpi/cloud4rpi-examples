# -*- coding: utf-8 -*-

from os import uname
from socket import gethostname
from time import sleep
import sys
import cloud4rpi
import chip
import ds18b20

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '__YOUR_DEVICE_TOKEN__'

# Constants
DATA_SENDING_INTERVAL = 30  # secs
DIAG_SENDING_INTERVAL = 60  # secs
POLL_INTERVAL = 0.5  # 500 ms


def main():
    # load w1 modules
    ds18b20.init_w1()

    # detect DS18B20 temperature sensors
    ds_sensors = ds18b20.DS18b20.find_all()

    # Put variable declarations here
    variables = {
        'Room Temp': {
            'type': 'numeric',
            'bind': ds_sensors[0]
        },
        # 'Outside Temp': {
        #     'type': 'numeric',
        #     'bind': ds_sensors[1]
        # },
        'CPU Temp': {
            'type': 'numeric',
            'bind': chip.cpu_temp
        }
    }

    # Put system data declarations here
    diagnostics = {
        'IP Address': chip.ip_address,
        'Host': gethostname(),
        'Operating System': " ".join(uname())
    }

    device = cloud4rpi.connect_mqtt(DEVICE_TOKEN)
    device.declare(variables)
    device.declare_diag(diagnostics)

    try:
        diag_timer = 0
        data_timer = 0
        while True:
            if data_timer <= 0:
                device.send_data()
                data_timer = DATA_SENDING_INTERVAL

            if diag_timer <= 0:
                device.send_diag()
                diag_timer = DIAG_SENDING_INTERVAL

            diag_timer -= POLL_INTERVAL
            data_timer -= POLL_INTERVAL
            sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.error("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
