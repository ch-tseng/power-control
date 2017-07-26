#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import datetime
import os.path as path
from datetime import date
import time
import calendar
from libraryCH.device.i2cLCD import i2cLCD
import subprocess

GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT)
GPIO.output(14, GPIO.LOW)

lcd = i2cLCD(addr=0x27, width=16)

startList = []
endList = []
powerStatus = False

lcd.display("Power Controller", 0)
lcd.display("made by CH.Tseng", 1)
time.sleep(3)
ii = 0
ii_net = 0
lastCMD = 0
lastDate = 0


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def getIP(interface):
    address = subprocess.check_output("/sbin/ifconfig " + interface + " | grep inet | grep -v inet6 | awk '{print $2}' | sed 's/addr://'i", shell=True)
    #address = address.decode('utf-8')
    return str(address)

def displayIP():
    global ii_net

    if(ii_net==0):
        lcd.display( getIP("eth0"), 0)
        ii_net = 1
    else:
        lcd.display( getIP("wlan0"), 0)
        ii_net = 0

#Read schedule file
def readSchedule():
    global startList, endList, lastDate
    my_date = date.today()

    if(my_date != lastDate):
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

        lastDate = my_date

while True:
    readSchedule()

    now = datetime.datetime.now().time()
    cmd = 0
    timeID = 0
    displayTXT = ""
    i = 0

    for startTime, endTime in zip(startList, endList):
       
        #print("startTime:{}, endTime:{}".format(startTime, endTime) )
        if(time_in_range(startTime, endTime, now) == True):
            cmd = cmd + 1
            displayTXT = " " + startTime.strftime('%H:%M') + " to " + endTime.strftime('%H:%M')

        i += 1

    if(lastCMD!=cmd):
        lcd.display(displayTXT , 1)
        lastCMD = cmd

        if(cmd > 0):
            if(powerStatus == False):
                GPIO.output(14, GPIO.HIGH)
                powerStatus = True
        else:
            if(powerStatus == True):
                GPIO.output(14, GPIO.LOW)
                powerStatus = False

        time.sleep(1)

    else:
        #print("i=",i)
        for id in range(i):
           now = datetime.datetime.now().time()

           start = startList[id]
           end = endList[id]
           #lcd.display("Next:"+start.strftime('%H:%M') + "-" + end.strftime('%H:%M'), 1)
           #print(startTime[id].strftime('%H:%M') + "-" + endTime[id].strftime('%H:%M'))
           if(ii%2 == 1):
               displayNow = now.strftime('%H %M')
               ii = 0
           else:
               displayNow =  now.strftime('%H:%M')
               ii = 1

           
           if(cmd>0):
               if(ii==0): 
                   displayIP()

               else:
                   lcd.display(displayNow + " ---> ON", 0)
                   lcd.display(displayTXT, 1)

           else:
               if(ii==0):
                   displayIP()
               else:
                   lcd.display(displayNow + " ---> OFF", 0)

               lcd.display("Next "+start.strftime('%H:%M') + "-" + end.strftime('%H:%M'), 1)

           time.sleep(1)
  
    #time.sleep(1)
