"""Tkinter"""

from Tkinter import *
import serial
import time
import struct
from xbee import ZigBee
import Buckets
import random

port = 'COM4'
baud_rate = 9600

ser = serial.Serial(port, baud_rate)
xbee = ZigBee(ser, escaped = True)

bucket_1 = Buckets.Buckets(1, '\x00\x13\xA2\x00\x40\xC3\x35\x3F', '\xFF\xFE', 2.2, 0, 'black', xbee)
bucket_2 = Buckets.Buckets(2, '\x00\x13\xA2\x00\x40\xCA\xAE\x7D', '\xFF\xFE', 2.2, 0, 'black', xbee)

bucket_1.filename = 'bucket1.csv'
bucket_2.filename = 'bucket2.csv'

bucket_1_file = open(bucket_1.filename, 'a')
bucket_2_file = open(bucket_2.filename, 'a')

bucket_1_file.write("--------------------------------------------------- \n")
bucket_1_file.write(time.strftime("%a, %d %b %Y %H:%M:%S \n"))
bucket_1_file.write("Weight(Grams), Density(GPM/Sqft/20min), ADC, Calb \n")
bucket_2_file.write("--------------------------------------------------- \n")
bucket_2_file.write(time.strftime("%a, %d %b %Y %H:%M:%S \n"))
bucket_2_file.write("Weight(Grams), Density(GPM/Sqft/20min), ADC, Calb \n")

initialize = 0

root = Tk()

topframe = Frame(root, bd=5,bg="white")
topframe.grid(row=0,column=0)

b1frame = Frame(topframe,  bd = 4 , bg = bucket_1.ledColor, relief = RAISED, padx=10,pady=10)
b2frame = Frame(topframe,  bd = 4 , bg = bucket_2.ledColor, relief = RAISED,padx=10,pady=10)

b1frame.grid(row = 0,column =0)
b2frame.grid(row =0,column=1)

bottomframe = Frame(root)
bottomframe.grid(row=1,column=0)

def update2():
    print "Reading bucket 2, wait..."
    bucket_2.readSensor(xbee)
    txt = (bucket_2.adcValue-bucket_2.tareValue)*float(b2m.get()) # + float(b2b.get())
    bucket_2.weightValue = float(txt)
    bucket_2.densityValue = calculateDensity(Grams = bucket_2.weightValue)
    bucket2Density.config(text=str("{:5.3f}".format(bucket_2.densityValue)))
    calculateColor(weightGRAMS=float(txt),bucket=bucket_2)
    b2frame.config(bg = bucket_2.ledColor)
    bucket2Grams.config(text=str(int(txt)))
    bucket_2.requestValveState(xbee)
    if bucket_2.valveState == "open":
        b2open.config(bg = "green")
        b2close.config(bg = "white")
    elif bucket_2.valveState == "close":
        b2open.config(bg = "white")
        b2close.config(bg = "green")
    elif bucket_2.valveState == "halfOpen":
        b2open.config(bg = "red")
        b2close.config(bg = "red")
    print "Done!"

def update1():
    print "Reading bucket 1, wait..."
    bucket_1.readSensor(xbee)
    txt = (bucket_1.adcValue-bucket_1.tareValue)*float(b1m.get()) # + float(b1b.get())
    bucket_1.weightValue = float(txt)
    bucket_1.densityValue = calculateDensity(Grams=bucket_1.weightValue)
    bucket1Density.config(text=str("{:5.3f}".format(bucket_1.densityValue)))
    calculateColor(weightGRAMS=float(txt),bucket=bucket_1)
    b1frame.config(bg = bucket_1.ledColor)
    bucket1Grams.config(text=str(int(txt)))
    bucket_1.requestValveState(xbee)
    if bucket_1.valveState == "open":
        b1open.config(bg = "green")
        b1close.config(bg = "white")
    elif bucket_1.valveState == "close":
        b1open.config(bg = "white")
        b1close.config(bg = "green")
    elif bucket_1.valveState == "halfOpen":
        b1open.config(bg = "red")
        b1close.config(bg = "red")
    print "Done!"

def Calibrate1():
    print "Calibrating bucket 1, wait..."
    update1()
    bucket_1.corr1 = float(calWeight1.get())/(bucket_1.adcValue-bucket_1.tareValue)
    b1m.delete(0,END)
    b1m.insert(0, str(bucket_1.corr1))
    print "Done Calibrating!"

def Calibrate2():
    print "Calibrating bucket 2, wait..."
    update2()
    bucket_2.corr1 = float(calWeight2.get())/(bucket_2.adcValue-bucket_2.tareValue)
    b2m.delete(0,END)
    b2m.insert(0, str(bucket_2.corr1))
    print "Done Calibrating!"

def calculateDensity(Grams,duration=20,area = 1):
    weightlbs = Grams*0.00220462
    gallons = weightlbs*0.11982844244
    density = gallons/area/duration
    return density

def calculateColor(weightGRAMS, duration = 20, area = 1, bucket=None):
    density = calculateDensity(weightGRAMS, duration, area)
    #print "density = " + str(density)
    if density >= 0.03:
        color = "blue"
    elif density >= 0.025 and density < 0.03:
        color = "green"
    elif density >= 0.02 and density <0.025:
        color = "cyan"
    elif density >=0.015 and density <0.02:
        color = "yellow"
    elif density >= -0.01 and density < 0.015:
        color = "red"
    else:
        color = "black"
    # print color
    bucket.ledColor = color

def nodeDiscovery():
    xbee.at(command = 'ND')
    time.sleep(0.2)
    try:
        response = xbee.wait_read_frame(20)
        if response['id'] == 'rx':
            pass
    except:
        pass

def writeToFile(file, bucket):
    file.write(str(bucket.weightValue)+', '+str(bucket.densityValue)+', '+str(bucket.adcValue)+', '+str(bucket.corr1)+'\n')
    pass

b1read = Button(bottomframe, text="read data", bg="white", font=("Helvetica", 20), command=update1)
b1open = Button(bottomframe, text="open valve", bg="white", font=("Helvetica", 20), command= lambda: bucket_1.openValve(xbee))
b1close = Button(bottomframe, text="close valve", bg="white", font=("Helvetica", 20), command= lambda: bucket_1.closeValve(xbee))
b1m = Entry(bottomframe, font=("Helvetica", 20))
b1m.insert(0, bucket_1.corr1)
saveButton1 = Button(bottomframe, text="Save 1", bg="white",font=("Helvetica", 20),command=lambda: writeToFile(bucket_1_file, bucket_1))
b1tare = Button(bottomframe, text="tare",bg = "white", font=("Helvetica", 20), command = lambda: bucket_1.tare(xbee))
calWeight1 = Entry(bottomframe, font=("Helvetica", 20))
calWeight1.insert(0, "Enter Weight (grams)")
b1cal = Button(bottomframe, text="Calibrate", bg = "white", font=("Helvetica", 20), command = Calibrate1)

b2read = Button(bottomframe, text="read data", bg="white", font=("Helvetica", 20), command=update2)
b2open = Button(bottomframe, text="open valve", bg="white", font=("Helvetica", 20), command=lambda: bucket_2.openValve(xbee))
b2close = Button(bottomframe, text="close valve", bg="white", font=("Helvetica", 20), command=lambda: bucket_2.closeValve(xbee))
b2m = Entry(bottomframe, font=("Helvetica", 20))
b2m.insert(0,bucket_2.corr1)
saveButton2 = Button(bottomframe, text="Save 2", bg="white",font=("Helvetica", 20),command=lambda: writeToFile(bucket_2_file, bucket_2))
b2tare = Button(bottomframe, text="tare",bg = "white", font=("Helvetica", 20), command = lambda: bucket_2.tare(xbee))
calWeight2 = Entry(bottomframe, font=("Helvetica", 20))
calWeight2.insert(0, "Enter Weight (grams)")
b2cal = Button(bottomframe, text="Calibrate",bg="white", font=("Helvetica", 20), command = Calibrate2)

bucket1Density = Label(b1frame, text="Bucket 1 (Density)",bg = "white", font=("Helvetica", 20))
bucket2Density = Label(b2frame, text="Bucket 2 (Density)",bg = "white", font=("Helvetica", 20))

bucket1Grams = Label(b1frame, text="Bucket 1 (Grams)",bg = "white", font=("Helvetica", 20))
bucket2Grams = Label(b2frame, text="Bucket 2 (Grams)",bg = "white", font=("Helvetica", 20))

bucket1Density.grid(row=0,column=0,padx=15,pady=20)
bucket2Density.grid(row=0,column=1,padx=15,pady=20)
bucket1Grams.grid(row=1,column=0,padx=15,pady=20)
bucket2Grams.grid(row=1,column=1,padx=15,pady=20)

b1read.grid(row=1, column=0,padx=5,pady=5)
b1open.grid(row=2,column=0)
b1close.grid(row=3,column=0)
#b1setcolor.grid(row=4,column=0)
b1m.grid(row=5,column=0)
saveButton1.grid(row=6,column=0)
b1tare.grid(row=7,column=0)
calWeight1.grid(row=8,column=0)
b1cal.grid(row=9,column=0)

b2read.grid(row=1, column=1,padx=5,pady=5)
b2open.grid(row=2,column=1)
b2close.grid(row=3,column=1)
#b2setcolor.grid(row=4,column=1)
b2m.grid(row=5,column=1)
saveButton2.grid(row=6,column=1)
b2tare.grid(row=7,column=1)
calWeight2.grid(row=8,column=1)
b2cal.grid(row=9,column=1)

if initialize == 0:
    pass


root.mainloop()

bucket_1_file.close()
bucket_2_file.close()
ser.close()
