#!/usr/bin/env python

# Based on previous work by
# Charles Menguy (see: http://stackoverflow.com/questions/10217067/implementing-a-full-python-unix-style-daemon-process)
# and Sander Marechal (see: http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)

# Adapted by M.Hendrix [2015,2016]

# daemon97.py pushes data to the MySQL-server.
# daemon23 support

import syslog, traceback
import os, sys, shutil, glob, time, subprocess
from libdaemon import Daemon
import ConfigParser
import MySQLdb as mdb

DEBUG = False
IS_SYSTEMD = os.path.isfile('/bin/journalctl')
leaf = os.path.realpath(__file__).split('/')[-2]

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
        print "Unexpected MySQL error"
        print "Error {0:d}: {1!s}".format(e.args[0], e.args[1])
      if consql:    # attempt to close connection to MySQLdb
        if DEBUG:print "Closing MySQL connection"
        consql.close()
        syslog.syslog(syslog.LOG_ALERT," ** Closed MySQL connection in run() **")
      syslog.syslog(syslog.LOG_ALERT,e.__doc__)
      syslog_trace(traceback.format_exc())
      raise

    iniconf = ConfigParser.ConfigParser()
    inisection = "97"
    home = os.path.expanduser('~')
    s = iniconf.read(home + '/' + leaf + '/config.ini')
    if DEBUG: print "config file : ", s
    if DEBUG: print iniconf.items(inisection)
    reportTime = iniconf.getint(inisection, "reporttime")
    cycles = iniconf.getint(inisection, "cycles")
    samplesperCycle = iniconf.getint(inisection, "samplespercycle")
    flock = iniconf.get(inisection, "lockfile")

    samples = samplesperCycle * cycles              # total number of samples averaged
    sampleTime = reportTime/samplesperCycle         # time [s] between samples
    cycleTime = samples * sampleTime                # time [s] per cycle

    myname = os.uname()[1]
    while True:
      try:
        startTime=time.time()

        do_sql_data(flock, iniconf, consql)

        waitTime = sampleTime - (time.time() - startTime) - (startTime%sampleTime)
        if (waitTime > 0):
          if DEBUG:print "Waiting {0} s".format(waitTime)
          time.sleep(waitTime)

      except Exception as e:
        if DEBUG:
          print "Unexpected error:"
          print e.message
        # attempt to close connection to MySQLdb
        if consql:
          if DEBUG:print "Closing MySQL connection"
          consql.close()
          syslog.syslog(syslog.LOG_ALERT," *** Closed MySQL connection in run() ***")
        syslog.syslog(syslog.LOG_ALERT,e.__doc__)
        syslog_trace(traceback.format_exc())
        raise

def cat(filename):
  ret = ""
  if os.path.isfile(filename):
    with open(filename,'r') as f:
      ret = f.read().strip('\n')
  return ret

def do_writesample(cnsql, cmd, sample):
  fail2write = False
  dat = (sample.split(', '))
  try:
    cursql = cnsql.cursor()
    if DEBUG:print "      ",dat
    cursql.execute(cmd, dat)
    cnsql.commit()
    cursql.close()
  except mdb.IntegrityError as e:
    if DEBUG:print e.args
    syslog.syslog(syslog.LOG_ALERT,e.__doc__)
    if cursql:
      if DEBUG:print " ** Closing MySQL connection"
      cursql.close()
      syslog.syslog(syslog.LOG_ALERT," ** Closed MySQL connection in do_writesample **")
      syslog.syslog(syslog.LOG_DEBUG,"{0}".format(dat))
    pass

  return fail2write

def do_sql_data(flock, inicnfg, cnsql):
  if DEBUG:
    print "============================"
    print "Pushing data to MySQL-server"
    print "============================"
  # set a lock
  lock(flock)
  time.sleep(2)
  # wait for all other processes to release their locks.
  count_internal_locks=2
  while (count_internal_locks > 1):
    time.sleep(1)
    count_internal_locks=0
    for fname in glob.glob(r'/tmp/' + leaf + '/*.lock'):
      count_internal_locks += 1
    if DEBUG:print "{0} internal locks exist".format(count_internal_locks)
  #endwhile

  for inisect in inicnfg.sections(): # Check each section of the config.ini file
    errsql = False
    try:
      ifile = inicnfg.get(inisect,"resultfile")
      if DEBUG:print " < ",ifile

      try:
        sqlcmd = []
        sqlcmd = inicnfg.get(inisect,"sqlcmd")
        if DEBUG:print "   ",sqlcmd

        data = cat(ifile).splitlines()
        if data:
          for entry in range(0, len(data)):
            errsql = do_writesample(cnsql, sqlcmd, data[entry])
          #endfor
        #endif
      except ConfigParser.NoOptionError as e:  #no sqlcmd
        if DEBUG:
          print "** ", e.message
    except ConfigParser.NoOptionError as e:  #no ifile
      if DEBUG:
        print "** ", e.message

    try:
      ofile = inicnfg.get(inisect,"rawfile")
      if DEBUG:print " > ",ofile
      if not errsql:                    # SQL-job was successful or non-existing
        if os.path.isfile(ifile):       # IF resultfile exists
          if not os.path.isfile(ofile): # AND rawfile does not exist
            shutil.move(ifile, ofile)   # THEN move the file over
    except ConfigParser.NoOptionError as e:  #no ofile
      if DEBUG:
        print "** ", e.message

  #endfor
  unlock(flock)

def lock(fname):
  open(fname, 'a').close()

def unlock(fname):
  if os.path.isfile(fname):
    os.remove(fname)

def syslog_trace(trace):
  #Log a python stack trace to syslog
  log_lines = trace.split('\n')
  for line in log_lines:
    if line:
      syslog.syslog(syslog.LOG_ALERT,line)

if __name__ == "__main__":
  daemon = MyDaemon('/tmp/' + leaf + '/97.pid')
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
