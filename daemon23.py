#!/usr/bin/env python

# Based on previous work by
# Charles Menguy (see: http://stackoverflow.com/questions/10217067/implementing-a-full-python-unix-style-daemon-process)
# and Sander Marechal (see: http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)

# Adapted by M.Hendrix [2016]

# daemon23.py measures the BMP183 pressure and temperature.
# uses moving averages

# Wiring :
# VIN              = P9_5  - VDD_5V
# 3Vo              = not connected
# GND              = P9_1  - DGND
# SCK              = P9_22 - SPI0_SCLK
# SDO              = P9_21 - SPI0_MISO
# SDI              = P9_18 - SPI0_MOSI
# CS               = P9_17 - SPI0_CS0

import syslog, traceback
import os, sys, time, math
import ConfigParser

from bbio import *
# Import the BMP183 class from the BMP183 library:
from bbio.libraries.BMP183 import BMP183

# own libraries:
from libdaemon import Daemon

DEBUG = False
IS_SYSTEMD = os.path.isfile('/bin/journalctl')
leaf = os.path.realpath(__file__).split('/').[-2]

# Create a new instance of the BMP183 class using SPI0 with the
# default CS0 chip select pin:
bmp = BMP183(SPI0)

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
BMP183T_gain = 1.0
BMP183P_gain = 1.0
# offset(old)
BMP183T_offset = -0.2
BMP183P_offset = 0.0

class MyDaemon(Daemon):
  def run(self):
    iniconf = ConfigParser.ConfigParser()
    inisection = "23"
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
  T0 = bmp.getTemp()
  P0 = bmp.getPressure()

  # Note that sometimes you won't get a reading and
  # the results will be null (because Linux can't
  # guarantee the timing of calls to read the sensor).
  # If this happens try again!
  if P0 is not None and T0 is not None:
    P = (P0 * BMP183P_gain + BMP183P_offset) / 100
    T = T0 * BMP183T_gain + BMP183T_offset
    D.append(T)
    D.append(P)
    if DEBUG:print '  T0 = {0:0.1f}*C        P0 = {1:0.1f}Pa'.format(T0, P0)
    if DEBUG:print 'Temp = {0:0.1f}*C  Pressure = {1:0.1f}mbar'.format(T, P)
  return D

def do_report(result, flock, fdata):
  # Get the time and date in human-readable form and UN*X-epoch...
  outDate = time.strftime('%Y-%m-%dT%H:%M:%S')
  outEpoch = int(time.strftime('%s'))
  # round to current minute to ease database JOINs
  outEpoch = outEpoch - (outEpoch % 60)
  fresult = ', '.join(map(str, result))
  lock(flock)
  f = file(fdata, 'a')
  f.write('{0}, {1}, {2}\n'.format(outDate, outEpoch, fresult) )
  f.close()
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
    if len(line):
      syslog.syslog(syslog.LOG_ALERT,line)

if __name__ == "__main__":
  daemon = MyDaemon('/tmp/' + leaf + '/23.pid')
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
    print "usage: %s start|stop|restart|foreground" % sys.argv[0]
    sys.exit(2)
