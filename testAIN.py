#!/usr/bin/env python
import Adafruit_BBIO.ADC as ADC
import time

sensor_pin = 'AIN6'
# sensor calibration data
#tmp36_mV2deg =
tmp36_gain = 1.0
tmp36_offset = 0.0

ADC.setup()

while True:
    reading = ADC.read(sensor_pin)
    millivolts = reading * 1800.0  # reference = 1800 mV
    temp_c = (millivolts - 500) / 10.0
    temp_c = temp_c * tmp36_gain + tmp36_offset

    raw_millivolt = ADC.read_raw(sensor_pin)
    temp_cr = (raw_millivolt - 500) / 10.0
    temp_cr = temp_cr * tmp36_gain + tmp36_offset
    print('mv=%d C=%.2f rw=%d Cr=%.2f' % (millivolts, temp_c, raw_millivolt, temp_cr))
    time.sleep(30)

# r
# mv = r * 1800
# c = (mv - 500) /10
#   = ((r * 1800) - 500) /10
#   = ((r * 180)  - 50)
