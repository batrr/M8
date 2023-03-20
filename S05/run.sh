#!/bin/sh

g++ -std=gnu++17 ticktock.cpp -o ticktock 

# ./ticktock  2>error.txt 1>output.txt 

cp ./ticktock /usr/sbin/ticktock
cp ./ticktock.service /etc/systemd/system/ticktock.service
chmod a+x /etc/systemd/system/ticktock.service

systemctl daemon-reload
systemctl restart ticktock
systemctl enable ticktock
systemctl status ticktock

journalctl -u ticktock -f
