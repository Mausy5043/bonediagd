#!/usr/bin/env python

# Based on previous work by
# Charles Menguy (see: http://stackoverflow.com/questions/10217067/implementing-a-full-python-unix-style-daemon-process)
# and Sander Marechal (see: http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)

# Adapted by M.Hendrix [2015]

# daemon11.py measures the CPU temperature.
# uses moving averages

import syslog, traceback
import os, sys, time, math
from libdaemon import Daemon

DEBUG = False
IS_SYSTEMD = os.path.isfile('/bin/journalctl')

class MyDaemon(Daemon):
  def run(self):
    sampleptr = 0
    reportTime = 60                                 # time [s] between reports
    cycles = 3                                      # number of cycles to aggregate
    samplesperCycle = 5                             # total number of samples in each cycle
    samples = samplesperCycle * cycles              # total number of samples averaged
    sampleTime = reportTime/samplesperCycle         # time [s] between samples
    cycleTime = samples * sampleTime                # time [s] per cycle

    data = []                                       # array for holding sampledata

    while True:
      try:
        startTime = time.time()

        result = do_work()
        if DEBUG:print result

        data.append(float(result))
        if (len(data) > samples):data.pop(0)
        sampleptr += 1

        # report sample average
        if (startTime % reportTime < sampleTime):
          if DEBUG:print data
          averages = sum(data[:]) / len(data)
          if DEBUG:print averages
          do_report(averages)
          if (sampleptr == samples):
            sampleptr = 0

        waitTime = sampleTime - (time.time() - startTime) - (startTime%sampleTime)
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
  Tcpu = "NaN"
  # Read the CPU temperature
  fi   = "/sys/class/hwmon/hwmon0/device/temp1_input"
  f    = file(fi,'r')
  Tcpu = float(f.read().strip('\n'))/1000
  f.close()
  if Tcpu > 75.000:
    # can't believe my sensors. Probably a glitch. Wait a while then measure again
    time.sleep(7)
    fi   = "/sys/class/hwmon/hwmon0/device/temp1_input"
    f    = file(fi,'r')
    Tcpu = float(f.read().strip('\n'))/1000
    Tcpu = float(Tcpu) + 0.1

  return Tcpu

def do_report(result):
  # Get the time and date in human-readable form and UN*X-epoch...
  outDate = time.strftime('%Y-%m-%dT%H:%M:%S, %s')
  flock = '/tmp/bonediagd/11.lock'
  lock(flock)
  f = file('/tmp/bonediagd/11-t-cpu.csv', 'a')
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
  daemon = MyDaemon('/tmp/bonediagd/11.pid')
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
