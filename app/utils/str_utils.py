import re


def clean_ble_message(message):
    return re.sub(r'[\t\r\n]+', '', message.decode('utf-8')).strip()
