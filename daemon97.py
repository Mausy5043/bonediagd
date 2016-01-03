#!/usr/bin/env python

# Based on previous work by
# Charles Menguy (see: http://stackoverflow.com/questions/10217067/implementing-a-full-python-unix-style-daemon-process)
# and Sander Marechal (see: http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)

# Adapted by M.Hendrix [2015,2016]

# daemon97.py pushes data to the MySQL-server.

import syslog, traceback
import os, sys, shutil, glob, time, commands, subprocess
from libdaemon import Daemon
import MySQLdb as mdb

DEBUG = False
IS_SYSTEMD = os.path.isfile('/bin/journalctl')

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

    samples = 1

    sampleTime = 60
    cycleTime = samples * sampleTime

    myname = os.uname()[1]
    while True:
      try:
        startTime=time.time()

        do_sql_data(remote_path)

        waitTime = sampleTime - (time.time() - startTime) - (startTime%sampleTime)
        if (waitTime > 0):
          if DEBUG:print "Waiting {0} s".format(waitTime)
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

def do_sql_data():
  if DEBUG:print("Pushing data to MySQL-server")
  return

def lock(fname):
  open(fname, 'a').close()

def unlock(fname):
  if os.path.isfile(fname):
    os.remove(fname)

def syslog_trace(trace):
  #Log a python stack trace to syslog
  log_lines = trace.split('\n')
  for line in log_lines:
    if len(line):
      syslog.syslog(syslog.LOG_ALERT,line)

if __name__ == "__main__":
  daemon = MyDaemon('/tmp/bonediagd/97.pid')
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
