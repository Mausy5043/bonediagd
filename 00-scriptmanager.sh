#!/bin/bash

# 00-scriptmanager.sh is run periodically by a private cronjob.
# * It synchronises the local copy of bonediagd with the current github branch
# * It checks the state of and (re-)starts daemons if they are not (yet) running.

CLNT=$(hostname)
branch=$(cat "$HOME/.bonediagd.branch")
pushd "$HOME/bonediagd"

 # force recompilation of libraries
 #rm ./*.pyc
 # Synchronise local copy with $branch

 git fetch origin
 # Check which code has changed
 # git diff --name-only
 # git log --graph --oneline --date-order --decorate --color --all

 DIFFlib=$(git --no-pager diff --name-only "$branch..origin/$branch" -- ./libdaemon.py)
 DIFFd11=$(git --no-pager diff --name-only "$branch..origin/$branch" -- ./daemon11.py)
 DIFFd12=$(git --no-pager diff --name-only "$branch..origin/$branch" -- ./daemon12.py)
 DIFFd13=$(git --no-pager diff --name-only "$branch..origin/$branch" -- ./daemon13.py)
 DIFFd14=$(git --no-pager diff --name-only "$branch..origin/$branch" -- ./daemon14.py)
 DIFFd15=$(git --no-pager diff --name-only "$branch..origin/$branch" -- ./daemon15.py)
 DIFFd21=$(git --no-pager diff --name-only "$branch..origin/$branch" -- ./daemon21.py)
 DIFFd22=$(git --no-pager diff --name-only "$branch..origin/$branch" -- ./daemon22.py)
 DIFFd23=$(git --no-pager diff --name-only "$branch..origin/$branch" -- ./daemon23.py)
 DIFFd97=$(git --no-pager diff --name-only "$branch..origin/$branch" -- ./daemon97.py)
 DIFFd98=$(git --no-pager diff --name-only "$branch..origin/$branch" -- ./daemon98.py)
 DIFFd99=$(git --no-pager diff --name-only "$branch..origin/$branch" -- ./daemon99.py)
 DIFFDHT=$(git --no-pager diff --name-only "$branch..origin/$branch" |grep -c "DHT22")

 git pull
 git fetch origin
 git checkout "$branch"
 git reset --hard "origin/$branch" && \
 git clean -f -d

#python -m compileall .
# Set permissions
chmod -R 744 ./*

if [[ ! -d /tmp/bonediagd ]]; then
  mkdir /tmp/bonediagd
fi

######## Install new libraries #######
echo "***"
echo "DHT22 changes: $DIFFDHT"
echo "***"
if [[ $DIFFDHT -ne 0 ]]; then
  pushd DHT22
  python setup.py install
  echo ""
  examples/simpletest.py
  echo ""
  popd
fi

######## Stop daemons ######

if [[ -n "$DIFFd11" ]]; then
  logger -p user.notice -t bonediagd "Source daemon11 has changed."
  ./daemon11.py stop
fi
if [[ -n "$DIFFd12" ]]; then
  logger -p user.notice -t bonediagd "Source daemon12 has changed."
  ./daemon12.py stop
fi
if [[ -n "$DIFFd13" ]]; then
  logger -p user.notice -t bonediagd "Source daemon13 has changed."
  ./daemon13.py stop
fi
if [[ -n "$DIFFd14" ]]; then
  logger -p user.notice -t bonediagd "Source daemon14 has changed."
  ./daemon14.py stop
fi
if [[ -n "$DIFFd15" ]]; then
  logger -p user.notice -t bonediagd "Source daemon15 has changed."
  ./daemon15.py stop
fi
if [[ -n "$DIFFd21" ]]; then
  logger -p user.notice -t bonediagd "Source daemon21 has changed."
  ./daemon21.py stop
fi
if [[ -n "$DIFFd22" ]]; then
  logger -p user.notice -t bonediagd "Source daemon22 has changed."
  ./daemon22.py stop
fi
if [[ -n "$DIFFd23" ]]; then
  logger -p user.notice -t bonediagd "Source daemon23 has changed."
  ./daemon23.py stop
fi
if [[ -n "$DIFFd97" ]]; then
  logger -p user.notice -t bonediagd "Source daemon97 has changed."
  ./daemon97.py stop
fi
if [[ -n "$DIFFd98" ]]; then
  logger -p user.notice -t bonediagd "Source daemon98 has changed."
  ./daemon98.py stop
fi
if [[ -n "$DIFFd99" ]]; then
  logger -p user.notice -t bonediagd "Source daemon99 has changed."
  ./daemon99.py stop
fi

if [[ -n "$DIFFlib" ]]; then
  logger -p user.notice -t bonediagd "Source libdaemon has changed."
  # stop all daemons
  ./daemon11.py stop
  ./daemon12.py stop
  ./daemon13.py stop
  ./daemon14.py stop
  ./daemon15.py stop
  ./daemon21.py stop
  ./daemon22.py stop
  ./daemon23.py stop
  ./daemon97.py stop
  ./daemon98.py stop
  ./daemon99.py stop
fi

######## (Re-)start daemons ######

function destale {
  if [ -e "/tmp/bonediagd/$1.pid" ]; then
    if ! kill -0 $(cat "/tmp/bonediagd/$1.pid")  > /dev/null 2>&1; then
      logger -p user.err -t bonediagd "Stale daemon$1 pid-file found."
      rm "/tmp/bonediagd/$1.pid"
      ./"daemon$1.py" start
    fi
  else
    logger -p user.warn -t bonediagd "Found daemon$1 not running."
    ./"daemon$1.py" start
  fi
}

destale 11
destale 12
destale 13
destale 14
destale 15
destale 97
destale 98
destale 99

case "$CLNT" in
  bbone )   echo "BeagleBone Black"
            destale 21
            destale 22
            destale 23
            #./testgraph.sh
            ;;
  * )       echo "!! undefined client !!"
            ;;
esac

popd

# the $MOUNTPOINT is in /etc/fstab
# in the unlikely event that the mount was lost,
# remount it here.
MOUNTPOINT=/mnt/share1
MOUNTDRIVE=boson.lan:/srv/array1/dataspool
if grep -qs $MOUNTPOINT /proc/mounts; then
    # It's mounted.
  echo "mounted"
else
    # Mount the share containing the data
    mount $MOUNTDRIVE $MOUNTPOINT
fi
