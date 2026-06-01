#!/bin/bash

cd ~/tg

git pull origin main

pip3 install -r requirements.txt

pkill -f bot.py

nohup python3 bot.py > bot.log 2>&1 &
