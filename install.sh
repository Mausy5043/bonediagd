#! /bin/bash

# `bonebian-ua-netinst` installs `boneboot` and makes sure it is run at the
# very first boot.

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
echo master > /home/$ME/.bonediagd.branch

if [ ! -d /etc/cron.d ]; then
  echo "Creating /etc/cron.d..."
  sudo mkdir /etc/cron.d
fi

# set a cronjob
echo "# m h dom mon dow user  command" | sudo tee /etc/cron.d/bonediagd
echo "42  * *   *   *   $ME    /home/$ME/bonediagd/00-scriptmanager.sh 2>&1 | logger -p info -t bonediagd" | sudo tee --append /etc/cron.d/bonediagd
echo "@reboot           $ME    sleep 60; /home/$ME/bonediagd/00-scriptmanager.sh 2>&1 | logger -p info -t bonediagd" | sudo tee --append /etc/cron.d/bonediagd

if [ ! -e /mnt/share1 ]; then
  echo "Creating mountpoint..."
  sudo mkdir /mnt/share1
fi

./00-scriptmanager.sh

echo -n "Finished installation of bonediagd on "
date
