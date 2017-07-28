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

#Pin for control relay module
GPIO.setup(14, GPIO.OUT)
GPIO.output(14, GPIO.LOW)

#location for schedule files
pathSchedule = "/boot/poweron/"

lcd = i2cLCD(addr=0x27, width=16)

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


class PowerRelay:
    def __init__(self, path_Schedule):
        self.startList = []
        self.endList = []
        self.powerStatus = False
        self.lastDate = 0
        self.pathSchedule = path_Schedule
        self.status = False
        self.lastStatus = False
        self.activeSchedule = ""
        self.scheduleList = ""

    def readSchedule(self):
        my_date = date.today()

        if(my_date != self.lastDate):
            fileName = calendar.day_name[my_date.weekday()]
            filePath = self.pathSchedule + fileName + ".txt"
            if(path.isfile(filePath)==False):
                fileName = "Others.txt"
                filePath = self.pathSchedule + fileName

            print(filePath)

            f = open(filePath,"r")
            self.startList = []
            self.endList = []

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

                self.startList.append(timeStart)
                self.endList.append(timeEnd)

            f.close()

            self.lastDate = my_date

    def updateActionTake(self):
        cmd = 0
        now = datetime.datetime.now().time()

        for startTime, endTime in zip(self.startList, self.endList):
            cmd = cmd + 1
            self.activeSchedule = " " + startTime.strftime('%H:%M') + " to " + endTime.strftime('%H:%M')

        if(cmd>0):
            self.powerStatus = True
        else:
            self.powerStatus = False



i = 0
TimerPower = PowerRelay(pathSchedule)

while True:
    TimerPower.readSchedule()
    TimerPower.updateActionTake()

    now = datetime.datetime.now()
    timeNow = now.strftime('%Y/%m/%d %H:%M')

#    if(TimerPower.powerStatus != TimerPower.lastStatus):
    statusPower="ON" if(TimerPower.powerStatus==True) else "OFF"

    line01 = "{}".format(timeNow)

    ii=0 if(i>len(TimerPower.startList)-1) else i

    timeStart = str(TimerPower.startList[ii])
    timeEnd = str(TimerPower.endList[ii])
    line02 = " ON:{}~{}".format(timeStart[:5], timeEnd[:5]) 


    lcd.display( line01, 0)
    lcd.display( line02, 1)

    i=0 if(i>len(TimerPower.startList)-1) else i+1

    print(i, ii)

    time.sleep(2)
   

