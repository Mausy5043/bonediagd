#!/usr/bin/env python

# Based on previous work by
# Charles Menguy (see: http://stackoverflow.com/questions/10217067/implementing-a-full-python-unix-style-daemon-process)
# and Sander Marechal (see: http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)

# Adapted by M.Hendrix [2015]

# daemon21.py measures the TMP36 temperature.
# uses moving averages

import syslog, traceback
import os, sys, time, math
import Adafruit_BBIO.ADC as ADC

from random import randint

from libdaemon import Daemon

DEBUG = False
IS_SYSTEMD = os.path.isfile('/bin/journalctl')

class MyDaemon(Daemon):
  def run(self):
    sampleptr = 0
    cycles = 3                                # number of cycles to aggregate
    samplesperCycle = 5                       # total number of samples in each cycle
    samples = samplesperCycle * cycles        # total number of samples averaged
    sampleTime = 60/samplesperCycle           # time [s] between samples
    cycleTime = samples * sampleTime          # time [s] per cycle
    reportTime = 1 * samplesperCycle * sampleTime                # time [s] between reports

    data = []                                 # array for holding sampledata

    # sync to whole minute
    ## FIXME: sync to cycletime  not to cycles*cycletime!
    # e.g. 5 cycles of 1' -> log every cycle (1').
    #waitTime = (cycleTime + sampleTime) - (time.time() % (cycleTime/cycles))
    #if DEBUG:
    #  print "NOT waiting {0} s.".format(waitTime)
    #else:
    #  time.sleep(waitTime)

    while True:
      try:
        startTime = time.time()

        # **** Get sample value
        result = do_work()
        if DEBUG:print result
        # **** Store sample value
        data.append(float(result))              # add a sample at the end
        if (len(data) > samples):data.pop(0)    # remove oldest sample from the start

        sampleptr = sampleptr + 1               #

        # report sample average
        if (startTime % reportTime < sampleTime):
          if DEBUG:print data
          averages = sum(data[:]) / len(data)
          if DEBUG:print averages
          do_report(averages)
          if (sampleptr == samples):
            sampleptr = 0

        waitTime = sampleTime - (time.time() - startTime) - (startTime%sampleTime)   # sync to sampleTime [s]
        if (waitTime > 0):
          if DEBUG:print "Waiting {0} s".format(waitTime)
          time.sleep(waitTime)
      except Exception as e:
        if DEBUG:
          print("Unexpected error:")
          print e.message
        syslog.syslog(syslog.LOG_ALERT,e.__doc__)
        syslog_trace(traceback.format_exc())
        raise

def syslog_trace(trace):
  '''Log a python stack trace to syslog'''
  log_lines = trace.split('\n')
  for line in log_lines:
    if len(line):
      syslog.syslog(syslog.LOG_ALERT,line)

def do_work():
  T = randint(0,9)
  return T

def do_report(result):
  # Get the time and date in human-readable form and UN*X-epoch...
  outDate = time.strftime('%Y-%m-%dT%H:%M:%S, %s')
  flock = '/tmp/bonediagd/21.lock'
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
  daemon = MyDaemon('/tmp/bonediagd/21.pid')
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
