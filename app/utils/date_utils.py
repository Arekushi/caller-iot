from machine import RTC


rtc = RTC()


def get_current_datetime_iso():
    rtc_datetime = rtc.datetime()

    year = rtc_datetime[0]
    month = rtc_datetime[1]
    day = rtc_datetime[2]
    hour = rtc_datetime[4] - 3
    minute = rtc_datetime[5]
    second = rtc_datetime[6]

    return '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(year, month, day, hour, minute, second)
