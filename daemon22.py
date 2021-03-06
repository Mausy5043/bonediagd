#!/usr/bin/env python

# Based on previous work by
# Charles Menguy (see: http://stackoverflow.com/questions/10217067/implementing-a-full-python-unix-style-daemon-process)
# and Sander Marechal (see: http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)

# Adapted by M.Hendrix [2015]

# daemon22.py measures the DHT22 humidity and temperature.
# uses moving averages

# Wiring (facing frontside of DHT22, left to right):
# PWR              = P9_4  - VDD_3V3
# data (digital)   = P8_15 - GPIO_47 & R=4k7 > VDD_3V3
# NC               = not connected
# GND              = P9_1  - DGND

import syslog, traceback
import os, sys, time, math
import ConfigParser
import bonediagd_DHT

# own libraries:
from libdaemon import Daemon

DEBUG = False
IS_SYSTEMD = os.path.isfile('/bin/journalctl')
leaf = os.path.realpath(__file__).split('/')[-2]

sensor_type = bonediagd_DHT.DHT22
sensor_pin  = 'P8_15'
# SENSOR CALIBRATION PROCEDURE
# Given the existing gain and offset.
# 1 Determine a linear least-squares fit between the output of this program and
#   data obtained from a reference sensor
# 2 The least-squares fit will yield the gain(calc) and offset(calc)
# 3 Determine gain(new) and offset(new) as shown here:
#     gain(new)   = gain(old)   * gain(calc)
#     offset(new) = offset(old) * gain(calc) + offset(calc)
# 4 Replace the existing values for gain(old) and offset(old) with the values
#   found for gain(new) and offset(new)

# gain(old)
DHT22T_gain = 1.0
DHT22H_gain = 1.0
# offset(old)
DHT22T_offset = -0.8
DHT22H_offset = 0.0

class MyDaemon(Daemon):
  def run(self):
    iniconf = ConfigParser.ConfigParser()
    inisection = "22"
    home = os.path.expanduser('~')
    s = iniconf.read(home + '/' + leaf + '/config.ini')
    if DEBUG: print "config file : ", s
    if DEBUG: print iniconf.items(inisection)
    reportTime = iniconf.getint(inisection, "reporttime")
    cycles = iniconf.getint(inisection, "cycles")
    samplesperCycle = iniconf.getint(inisection, "samplespercycle")
    flock = iniconf.get(inisection, "lockfile")
    fdata = iniconf.get(inisection, "resultfile")

    samples = samplesperCycle * cycles              # total number of samples averaged
    sampleTime = reportTime/samplesperCycle         # time [s] between samples
    cycleTime = samples * sampleTime                # time [s] per cycle

    data = []                                       # array for holding sampledata

    while True:
      try:
        startTime = time.time()

        # **** Get sample value
        result = do_work()
        if DEBUG:print result
        # **** Store sample value
        if result:
          data.append(map(float,result))              # add a sample at the end
          if (len(data) > samples):data.pop(0)        # remove oldest sample from the start

        # report sample average
        if (startTime % reportTime < sampleTime):   # sync reports to reportTime
          if DEBUG:print data
          # for single parameter arrays:
          #averages = sum(data[:]) / len(data)
          # for multiple parameter arrays:
          somma = map(sum,zip(*data))
          averages = [format(s / len(data), '.2f') for s in somma]
          if DEBUG:print averages
          do_report(averages, flock, fdata)

        waitTime = sampleTime - (time.time() - startTime) - (startTime%sampleTime)
        if (waitTime > 0):                          # sync to sampleTime [s]
          if DEBUG:print "Waiting {0} s".format(waitTime)
          time.sleep(waitTime)
      except Exception as e:
        if DEBUG:
          print "Unexpected error:"
          print e.message
        syslog.syslog(syslog.LOG_ALERT,e.__doc__)
        syslog_trace(traceback.format_exc())
        raise

def do_work():
  D = []
  # Try to grab a sensor reading.  Use the read_retry method which will retry up
  # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
  H0, T0 = bonediagd_DHT.read_retry(sensor_type, sensor_pin)

  # Note that sometimes you won't get a reading and
  # the results will be null (because Linux can't
  # guarantee the timing of calls to read the sensor).
  # If this happens try again!
  if H0 is not None and T0 is not None:
    H = H0 * DHT22H_gain + DHT22H_offset
    T = T0 * DHT22T_gain + DHT22T_offset
    D.append(T)
    D.append(H)
    if DEBUG:print '  T0 = {0:0.1f}*C        H0 = {1:0.1f}%'.format(T0, H0)
    if DEBUG:print 'Temp = {0:0.1f}*C  Humidity = {1:0.1f}%'.format(T, H)
  return D

def do_report(result, flock, fdata):
  # Get the time and date in human-readable form and UN*X-epoch...
  outDate = time.strftime('%Y-%m-%dT%H:%M:%S')
  outEpoch = int(time.strftime('%s'))
  # round to current minute to ease database JOINs
  outEpoch = outEpoch - (outEpoch % 60)
  fresult = ', '.join(map(str, result))
  lock(flock)
  with open(fdata, 'a') as f:
    f.write('{0}, {1}, {2}\n'.format(outDate, outEpoch, fresult) )
  unlock(flock)

def lock(fname):
  open(fname, 'a').close()

def unlock(fname):
  if os.path.isfile(fname):
    os.remove(fname)

def syslog_trace(trace):
  # Log a python stack trace to syslog
  log_lines = trace.split('\n')
  for line in log_lines:
    if line:
      syslog.syslog(syslog.LOG_ALERT,line)

if __name__ == "__main__":
  daemon = MyDaemon('/tmp/' + leaf + '/22.pid')
  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      daemon.start()
    elif 'stop' == sys.argv[1]:
      daemon.stop()
    elif 'restart' == sys.argv[1]:
      daemon.restart()
    elif 'foreground' == sys.argv[1]:
      # assist with debugging.
      print "Debug-mode started. Use <Ctrl>+C to stop."
      DEBUG = True
      if DEBUG:
        logtext = "Daemon logging is ON"
        syslog.syslog(syslog.LOG_DEBUG, logtext)
      daemon.run()
    else:
      print "Unknown command"
      sys.exit(2)
    sys.exit(0)
  else:
    print "usage: {0!s} start|stop|restart|foreground".format(sys.argv[0])
    sys.exit(2)
