#!/usr/bin/env python

# Based on previous work by
# Charles Menguy (see: http://stackoverflow.com/questions/10217067/implementing-a-full-python-unix-style-daemon-process)
# and Sander Marechal (see: http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)

# Adapted by M.Hendrix [2015]

# daemon21.py measures the TMP36 temperature.
# uses moving averages

import syslog, traceback
import os, sys, time, math
import Adafruit_BBIO.ADC  as ADC
import Adafruit_BBIO.GPIO as GPIO
import MySQLdb as mdb

# own libraries:
from libdaemon import Daemon

DEBUG = False
IS_SYSTEMD = os.path.isfile('/bin/journalctl')

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
TMP36_gain = 0.1
# offset(old)
TMP36_offset = -50.0



class MyDaemon(Daemon):
  def run(self):
    try:              # Initialise MySQLdb
      consql = mdb.connect(host='sql.lan', db='domotica', read_default_file='~/.my.cnf')

      if consql.open: # Hardware initialised succesfully -> get a cursor on the DB.
        cursql = consql.cursor()
        cursql.execute("SELECT VERSION()")
        versql = cursql.fetchone()
        cursql.close()
        logtext = "{0} : {1}".format("Attached to MySQL server", versql)
        syslog.syslog(syslog.LOG_INFO, logtext)
    except mdb.Error, e:
      if DEBUG:
        print("Unexpected MySQL error")
        print "Error %d: %s" % (e.args[0],e.args[1])
      if consql:    # attempt to close connection to MySQLdb
        if DEBUG:print("Closing MySQL connection")
        consql.close()
        syslog.syslog(syslog.LOG_ALERT,"Closed MySQL connection")
      syslog.syslog(syslog.LOG_ALERT,e.__doc__)
      syslog_trace(traceback.format_exc())
      raise

    try:      # Initialise hardware
      ADC.setup()
      GPIO.setup("USR0", GPIO.OUT)
    except Exception as e:
      if DEBUG:
        print("Unexpected error:")
        print e.message
      if consql:    # attempt to close connection to MySQLdb
        if DEBUG:print("Closing MySQL connection")
        consql.close()
        syslog.syslog(syslog.LOG_ALERT,"Closed MySQL connection")
      syslog.syslog(syslog.LOG_ALERT,e.__doc__)
      syslog_trace(traceback.format_exc())
      raise


    # Initialise parameters
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

        GPIO.output("USR0", GPIO.HIGH)

        # **** Get sample value
        result = do_work()
        if DEBUG:print result
        # **** Store sample value
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
          do_report(averages, consql)

        waitTime = sampleTime - (time.time() - startTime) - (startTime%sampleTime)
        if (waitTime > 0):                          # sync to sampleTime [s]
          if DEBUG:print "Waiting {0} s".format(waitTime)
          GPIO.output("USR0", GPIO.LOW)
          time.sleep(waitTime)
      except Exception as e:
        if DEBUG:
          print("Unexpected error:")
          print e.message
        # attempt to close connection to MySQLdb
        if consql:
          if DEBUG:print("Closing MySQL connection")
          consql.close()
          syslog.syslog(syslog.LOG_ALERT,"Closed MySQL connection")
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
  D = []
  V = ADC.read_raw(sensor_pin)
  D.append(V)
  T = V * TMP36_gain + TMP36_offset
  D.append(T)
  return D

def do_report(result,cnsql):
  # Get the time and date in human-readable form and UN*X-epoch...
  outDate = time.strftime('%Y-%m-%dT%H:%M:%S, %s')
  fresult = ', '.join(map(str, result))
  flock = '/tmp/bonediagd/21.lock'
  lock(flock)
  f = file('/tmp/TMP36.csv', 'a')
  f.write('{0}, {1}\n'.format(outDate, fresult) )
  f.close()
  unlock(flock)

  t_sample=outDate.split(',')
  cursql = cnsql.cursor()
  cmd = ('INSERT INTO tmp36 '
                    '(sample_time, sample_epoch, raw_value, temperature) '
                    'VALUES (%s, %s, %s, %s)')
  dat = (t_sample[0], int(t_sample[1]), result[0], result[1] )
  cursql.execute(cmd, dat)
  cnsql.commit()
  cursql.close()
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
