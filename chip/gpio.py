# -*- coding: utf-8 -*-

from os import uname
from socket import gethostname
from time import sleep
import sys
import cloud4rpi
import chip

# Get the GPIO module here: https://github.com/xtacocorex/CHIP_IO
import CHIP_IO.GPIO as GPIO  # pylint: disable=F0401

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '__YOUR_DEVICE_TOKEN__'

# Constants
POLL_INTERVAL = 0.5  # 500 ms
DATA_SENDING_INTERVAL = 30  # seconds * POLL_INTERVAL
DIAG_SENDING_INTERVAL = 60  # seconds * POLL_INTERVAL


def P0_control(value):
    GPIO.output('XIO-P0', value)
    return GPIO.input('XIO-P0')

GPIO.setup('XIO-P0', GPIO.OUT)


def main():
    # Put variable declarations here
    variables = {
        'XIO-P0': {
            'type': 'bool',
            'value': False,
            'bind': P0_control
        }
    }

    # Put system data declarations here
    diagnostics = {
        'IP Address': chip.ip_address,
        'Host': gethostname(),
        'Operating System': " ".join(uname()),
        'CPU Temperature': chip.cpu_temp
    }

    device = cloud4rpi.Device()
    device.declare(variables)
    device.declare_diag(diagnostics)

    api = cloud4rpi.connect_mqtt(DEVICE_TOKEN)
    api.on_command = device.handle_mqtt_commands(api)
    cfg = device.read_config()
    api.publish_config(cfg)

    # Adds a 1 second delay to ensure device variables are created
    sleep(1)

    try:
        diag_timer = 0
        data_timer = 0
        while True:
            if data_timer <= 0:
                data = device.read_data()
                api.publish_data(data)
                data_timer = DATA_SENDING_INTERVAL

            if diag_timer <= 0:
                diag = device.read_diag()
                api.publish_diag(diag)
                diag_timer = DIAG_SENDING_INTERVAL

            diag_timer -= POLL_INTERVAL
            data_timer -= POLL_INTERVAL
            sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')
        sys.exit(0)

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.error("ERROR! %s %s", error, sys.exc_info()[0])
        sys.exit(1)


if __name__ == '__main__':
    main()
