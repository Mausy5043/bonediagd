#!/usr/bin/env python
import Adafruit_BBIO.ADC as ADC
import time, commands, os

sensor_pin = 'AIN6'
# sensor calibration data
#tmp36_mV2deg =

# TMP36   DS18
# 17.86    19.16

tmp36_gain = 1.115
tmp36_offset = -0.58

ADC.setup()

def mV2degC(millivolt):
  degC = (millivolt - 500.0) / 10.0
  degC = (degC * tmp36_gain) + tmp36_offset
  return degC

def do_report(result):
  # Get the time and date in human-readable form and UN*X-epoch...
  outDate = commands.getoutput("date '+%FT%H:%M:%S, %s'")
  flock = '/tmp/TMP36.lock'
  lock(flock)
  f = file('/tmp/TMP36.csv', 'a')
  f.write('{0}, {1}\n'.format(outDate, float(result)) )
  f.close()
  unlock(flock)
  return

def lock(fname):
  open(fname, 'a').close()

def unlock(fname):
  if os.path.isfile(fname):
    os.remove(fname)

if __name__ == "__main__":

  while True:
    #reading = ADC.read(sensor_pin)
    #millivolts = reading * 1800.0  # reference = 1800 mV
    #temp_c = mV2degC(millivolts)
    #temp_c = (millivolts - 500) / 10.0
    #temp_c = temp_c * tmp36_gain + tmp36_offset

    raw_millivolt = ADC.read_raw(sensor_pin)
    temp_cr = mV2degC(raw_millivolt)
    #temp_cr = (raw_millivolt - 500) / 10.0
    #temp_cr = temp_cr * tmp36_gain + tmp36_offset
    #print('mv=%d C=%.2f rw=%d Cr=%.2f' % (millivolts, temp_c, raw_millivolt, temp_cr))
    do_report(temp_cr)
    time.sleep(60)
