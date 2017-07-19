import RPi.GPIO as GPIO
import datetime
import os.path as path
from datetime import date
import calendar

GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT)
GPIO.output(14, GPIO.LOW)

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

my_date = date.today()
fileName = calendar.day_name[my_date.weekday()] + ".txt"
if(path.isfile(fileName)==False): fileName="Others.txt"
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

while True:
    now = datetime.datetime.now().time()
    cmd = 0

    for startTime, endTime in zip(startList, endList):

        if(time_in_range(startTime, endTime, now) == True):
            cmd = cmd + 1

        #print("TimeNow:{}, StartTime:{}, EndTime:{}, PowerStatus:{} , CMD:{}".format(now, startTime, endTime, powerStatus, cmd))

    if(cmd > 0):
        if(powerStatus == False):
            GPIO.output(14, GPIO.HIGH)
            powerStatus = True
    else:
        if(powerStatus == True):
            GPIO.output(14, GPIO.LOW)
            powerStatus = False

