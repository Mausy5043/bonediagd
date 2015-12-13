#!/usr/bin/env python
import Adafruit_BBIO.ADC as ADC
import time

sensor_pin = 'AIN6'
# sensor calibration data
tmp36_gain = 1.0
tmp36_offset = 0.0

ADC.setup()

while True:
    reading = ADC.read(sensor_pin)
    raw_reading = ADC.raw_read(sensor_pin)
    millivolts = reading * 1800  # reference = 1800 mV
    temp_c = (millivolts - 500) / 10
    temp_c = temp_c * tmp36_gain + tmp36_offset
    temp_f = (temp_c * 9/5) + 32
    print('rw=%d mv=%d C=%.2f F=%d' % (raw_reading, millivolts, temp_c, temp_f))
    time.sleep(1)
