import Adafruit_BBIO.ADC as ADC
import time

sensor_pin = 'AIN6'

ADC.setup()

while True:
    reading = ADC.read(sensor_pin)
    raw_reading = ADC.read_raw(sensor_pin)
    millivolts = reading * 1800  # reference = 1800 mV
    temp_c = (millivolts - 500) / 10
    temp_f = (temp_c * 9/5) + 32
    print('rw=%d mv=%d C=%d F=%d' % (raw_reading, millivolts, temp_c, temp_f))
    time.sleep(1)
