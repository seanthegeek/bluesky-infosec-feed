#!/usr/bin/env bash

set -e

echo "Installing git..."
sudo apt install -y git
echo "Installing python3-virtualenv..."
sudo apt install -y python3-virtualenv
echo "Installing redis..."
sudo apt install -y redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
if [ ! -d "/opt/blueskyinfosecfeed/" ]; then
     echo "creating blueskyinfosecfeed user..."
     sudo useradd -r -m blueskyinfosecfeed -b /opt
fi

cd ~blueskyinfosecfeed
if [ ! -d "bluesky-infosec-feed" ]; then
    sudo -u blueskyinfosecfeed git clone https://github.com/seanthegeek/bluesky-infosec-feed
fi
cd bluesky-infosec-feed
sudo -u blueskyinfosecfeed git pull
sudo -u blueskyinfosecfeed setupvenv.sh
sudo cp systemd/* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable blueskyinfosecfeed.service
sudo systemctl restart blueskyinfosecfeed.service
sudo systemctl enable update-blueskyinfosecfeed.timer
sudo systemctl restart update-blueskyinfosecfeed.timer
