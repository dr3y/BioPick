#!/bin/sh
cp jnotebook.service /etc/systemd/system/jnotebook.service

systemctl enable jnotebook
systemctl start jnotebook