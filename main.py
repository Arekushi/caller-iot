import gc
import time
import network
from machine import Pin


led = Pin(2, Pin.OUT)


def turn_on_led():
    led.value(1)
    time.sleep(1)


def turn_off_led():
    led.value(0)


def connect():
    import utime
    import ntptime
    import app.secrets as secrets

    print('Memory free:', gc.mem_free())
    turn_on_led()

    sta_if = network.WLAN(network.STA_IF)
    start = utime.time()
    timed_out = False

    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.connect(
            secrets.wifi_config['ssid'],
            secrets.wifi_config['password']
        )

        while not sta_if.isconnected() and not timed_out:
            if utime.time() - start >= 20:
                timed_out = True
            else:
                pass

    if sta_if.isconnected():
        ntptime.settime()
        print('Network Config:', sta_if.ifconfig())
        return True
    else:
        print('Internet not available!')
        return False


def update_code():
    import machine
    from ota_config import ota_config
    from app.http.ota_updater import OTAUpdater

    if connect():
        ota_updater = OTAUpdater(
            github_repo=ota_config['repo_url'],
            main_dir=ota_config['main_dir'],
            secrets_file=ota_config['secrets_file']
        )

        has_updated = ota_updater.install_update_if_available()

        if has_updated:
            machine.reset()
        else:
            del(ota_updater)
            gc.collect()
    else:
        print('Cannot update code!')


def start_app():
    from app.main import run

    turn_off_led()
    run()


update_code()
start_app()
