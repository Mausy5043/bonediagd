#!/usr/bin/env python
import Adafruit_BBIO.ADC as ADC
import time, os

sensor_pin = 'AIN6'
# SENSOR CALIBRATION PROCEDURE
# Given the existing gain and offset.
# 1 Determine a linear least-squares fit between the output of this program and
#   data obtained from the selected reference
# 2 The least-squares fit will yield the gain(calc) and offset(calc)
# 3 Determine gain(new) and offset(new) as shown here:
#     gain(new)   = gain(old)   * gain(calc)
#     offset(new) = offset(old) * gain(calc) + offset(calc)
# 4 Replace the existing values for gain(old) and offset(old) with the values
#   found for gain(new) and offset(new)

# gain(old)
TMP36_gain = 1.0
# offset(old)
TMP36_offset = 0.0

ADC.setup()

def mV2degC(millivolt):
  degC = (millivolt * TMP36_gain) + TMP36_offset
  return degC

def do_report(result):
  # Get the time and date in human-readable form and UN*X-epoch...
  outDate = time.strftime('%Y-%m-%dT%H:%M:%S, %s')
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
    rawMillivolt = ADC.read_raw(sensor_pin)
    temperature = mV2degC(rawMillivolt)
    do_report(temperature)
    time.sleep(60)
