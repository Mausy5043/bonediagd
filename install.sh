#!/bin/bash

# 'boneboot' is manually installed and run.

# `boneboot` then installs additional packages and modifies the system
# configuration accordingly. Among others, `bonediagd` may be installed
# using `git clone`. Followed by calling this `install.sh` script
ME=$(whoami)
# Installing `bonediagd` requires:
# 1. Add a cronjob in `/etc/cron.d/` periodically running `00-scriptmanager`
#    to keep the daemons up-to-date
# 2. Add various start-stop scripts to `/etc/init.d/` to start the daemons
#    automagically at re-boot. (currently using a cronjob)

echo -n "Started installing bonediagd on "
date
# To suppress git detecting changes by chmod:
git config core.fileMode false
# set the branch
echo "master" > "$HOME/.bonediagd.branch"

if [ ! -d /etc/cron.d ]; then
  echo "Creating /etc/cron.d..."
  mkdir /etc/cron.d
fi

# set a cronjob
echo "# m h dom mon dow user  command" | tee /etc/cron.d/bonediagd
echo "42  * *   *   *   $ME    $HOME/bonediagd/00-scriptmanager.sh 2>&1 | logger -p info -t bonediagd" | tee --append /etc/cron.d/bonediagd
echo "*/5  * *   *   *  $ME    $HOME/bonediagd/testgraph.sh 2>&1 | logger -p info -t testgraphs" | tee --append /etc/cron.d/bonediagd
echo "@reboot           $ME    sleep 120; $HOME/bonediagd/00-scriptmanager.sh 2>&1 | logger -p info -t bonediagd" | tee --append /etc/cron.d/bonediagd
echo "@reboot           $ME    echo nocape-w1 > /sys/devices/bone_capemgr.9/slots" | tee --append /etc/cron.d/bonediagd

if [ ! -e /mnt/share1 ]; then
  echo "Creating mountpoint..."
  mkdir /mnt/share1
fi

echo "Installing DHT22 support..."
pushd ./DHT22
  python setup.py install
  echo ""
  examples/simpletest.py
  echo ""
popd

echo "Installing 1-wire support..."
# source: http://www.bonebrews.com/temperature-monitoring-with-the-ds18b20-on-a-beaglebone-black/
pushd /tmp
wget -c https://raw.githubusercontent.com/RobertCNelson/tools/master/pkgs/dtc.sh
chmod +x dtc.sh
./dtc.sh
popd
/usr/local/bin/dtc -O dtb -o /lib/firmware/nocape-w1-00A0.dtbo -b 0 -@ nocape-w1.dts

echo nocape-w1 > /sys/devices/bone_capemgr.9/slots
cat /sys/devices/bone_capemgr.9/slots
#la  /sys/devices/w1_bus_master1
cat /sys/bus/w1/devices/28-*/w1_slave

echo "Patch BMP183.py"

# /usr/local/lib/python2.7/dist-packages/bbio/libraries/BMP183/BMP183.py
# https://github.com/graycatlabs/PyBBIO/issues/79

./00-scriptmanager.sh

echo -n "Finished installation of bonediagd on "
date
