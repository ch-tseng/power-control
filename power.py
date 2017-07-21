#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import datetime
import os.path as path
from datetime import date
import time
import calendar
from libraryCH.device.i2cLCD import i2cLCD

GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT)
GPIO.output(14, GPIO.LOW)

lcd = i2cLCD(addr=0x27, width=16)

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

my_date = date.today()
fileName = "/boot/poweron/" + calendar.day_name[my_date.weekday()] + ".txt"
if(path.isfile(fileName)==False): fileName="/boot/poweron/Others.txt"
print(fileName)

f = open(fileName,"r")
startList = []
endList = []

for line in f:
    lineString = line.replace("\n","")
    (startTime, endTime)  = (lineString.split("~"))
    hms_s = startTime.split(":")
    hms_e = endTime.split(":")

    if(int(hms_s[0])>23): hms_s[0]="23"
    if(int(hms_e[0])>23): hms_e[0]="23"
    if(int(hms_s[1])>59): hms_s[1]="59"
    if(int(hms_e[1])>59): hms_e[1]="59"
    if(int(hms_s[2])>59): hms_s[2]="59"
    if(int(hms_e[2])>59): hms_e[2]="59"


    timeStart = datetime.time(int(hms_s[0]), int(hms_s[1]), int(hms_s[2]))
    timeEnd = datetime.time(int(hms_e[0]), int(hms_e[1]), int(hms_e[2]))

    startList.append(timeStart)
    endList.append(timeEnd)

f.close()

powerStatus = False

#lcd.display("Good morning!", 1)
#lcd.clear()
lcd.display("Power Controller", 0)
lcd.display("made by CH.Tseng", 1)
time.sleep(3)

lastCMD = 0

while True:
    now = datetime.datetime.now().time()
    cmd = 0
    timeID = 0
    displayTXT = ""
    i = 0

    for startTime, endTime in zip(startList, endList):
       
        #print("startTime:{}, endTime:{}".format(startTime, endTime) )
        if(time_in_range(startTime, endTime, now) == True):
            cmd = cmd + 1
            displayTXT = "ON: " + startTime.strftime('%H:%M') + "-" + endTime.strftime('%H:%M')

        i += 1

    if(lastCMD!=cmd):
        print(displayTXT )
        lcd.display(displayTXT , 0)
        lastCMD = cmd

        if(cmd > 0):
            if(powerStatus == False):
                GPIO.output(14, GPIO.HIGH)
                powerStatus = True
        else:
            if(powerStatus == True):
                GPIO.output(14, GPIO.LOW)
                powerStatus = False

    else:
        if(cmd==0): lcd.display("Power is off now", 0)
        for id in range(i):
           print("i={}, len={}".format(id,len(startList)))
           start = startList[id]
           end = endList[id]
           lcd.display("Next:"+start.strftime('%H:%M') + "-" + end.strftime('%H:%M'), 1)
           #print(startTime[id].strftime('%H:%M') + "-" + endTime[id].strftime('%H:%M'))
           time.sleep(1)
