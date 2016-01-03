#!/usr/bin/env python

# Based on previous work by
# Charles Menguy (see: http://stackoverflow.com/questions/10217067/implementing-a-full-python-unix-style-daemon-process)
# and Sander Marechal (see: http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)

# Adapted by M.Hendrix [2015]

# daemon98.py uploads data to the server.

import syslog, traceback
import os, sys, shutil, glob, platform, time, commands, subprocess
from libdaemon import Daemon

DEBUG = False
IS_SYSTEMD = os.path.isfile('/bin/journalctl')

class MyDaemon(Daemon):
  def run(self):
    samples = 1

    sampleTime = 60
    cycleTime = samples * sampleTime

    myname = os.uname()[1]
    mount_path = '/mnt/share1/'
    remote_path = mount_path + myname
    remote_lock = remote_path + '/client.lock'
    while True:
      try:
        startTime=time.time()

        if os.path.ismount(mount_path):
          #print 'dataspool is mounted'
          do_mv_data(remote_path)

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
  #Log a python stack trace to syslog
  log_lines = trace.split('\n')
  for line in log_lines:
    if len(line):
      syslog.syslog(syslog.LOG_ALERT,line)

def do_mv_data(rpath):
  hostlock = rpath + '/host.lock'
  clientlock = rpath + '/client.lock'
  count_internal_locks=1

  # wait 3 seconds for processes to finish
  time.sleep(3)

  while os.path.isfile(hostlock):
    # wait while the server has locked the directory
    time.sleep(1)

  # server already sets the client.lock. Do it anyway.
  lock(clientlock)

  # prevent race conditions
  while os.path.isfile(hostlock):
    # wait while the server has locked the directory
    time.sleep(1)

  while (count_internal_locks > 0):
    time.sleep(1)
    count_internal_locks=0
    for file in glob.glob(r'/tmp/bonediagd/*.lock'):
      count_internal_locks += 1

  for file in glob.glob(r'/tmp/bonediagd/*.csv'):
    #print file
    if os.path.isfile(clientlock):
      if not (os.path.isfile(rpath + "/" + os.path.split(file)[1])):
        shutil.move(file, rpath)

  for file in glob.glob(r'/tmp/bonediagd/*.png'):
    if os.path.isfile(clientlock):
      shutil.move(file, rpath)

  unlock(clientlock)

  return

def lock(fname):
  open(fname, 'a').close()

def unlock(fname):
  if os.path.isfile(fname):
    os.remove(fname)

if __name__ == "__main__":
  daemon = MyDaemon('/tmp/bonediagd/98.pid')
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