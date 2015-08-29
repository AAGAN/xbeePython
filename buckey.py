﻿"""Tkinter"""

from Tkinter import *
import serial
import time
import struct
from xbee import ZigBee
import Buckets
import random

port = 'COM29'
baud_rate = 9600

ser = serial.Serial(port, baud_rate)
xbee = ZigBee(ser, escaped = True)

bucket_1 = Buckets.Buckets(1, '\x00\x13\xA2\x00\x40\xC3\x35\x3F', '\xFF\xFE', 1, 0, 'black', xbee)
bucket_2 = Buckets.Buckets(2, '\x00\x13\xA2\x00\x40\xCA\xAE\x7D', '\xFF\xFE', 2.2, 0, 'black', xbee)

root = Tk()

topframe = Frame(root, bd=5,bg="white")
topframe.grid(row=0,column=0)

b1frame = Frame(topframe, height = 100, width = 100 , bd = 4 , bg = bucket_1.ledColor, relief = RAISED, padx=10,pady=10)
b2frame = Frame(topframe, height = 100, width = 100 , bd = 4 , bg = bucket_2.ledColor, relief = RAISED,padx=10,pady=10)

b1frame.grid(row = 0,column =0)
b2frame.grid(row =0,column=1)

bottomframe = Frame(root)
bottomframe.grid(row=1,column=0)

def update2():
    bucket_2.readSensor(xbee)
    txt = (bucket_2.adcValue-bucket_2.tareValue)*float(b2m.get()) + float(b2b.get())
    bucket2.config(text=str(calculateDensity(Grams=float(txt))))
    calculateColor(weightGRAMS=float(txt),bucket=bucket_2)
    b2frame.config(bg = bucket_2.ledColor)
    calWeight2.delete(0,END)
    calWeight2.insert(0, str(txt))

def update1():
    bucket_1.readSensor(xbee)
    txt = (bucket_1.adcValue-bucket_1.tareValue)*float(b1m.get()) + float(b1b.get())
    bucket1.config(text=str(calculateDensity(Grams=float(txt))))
    calculateColor(weightGRAMS=float(txt),bucket=bucket_1)
    b1frame.config(bg = bucket_1.ledColor)
    calWeight1.delete(0,END)
    calWeight1.insert(0,str(txt))

def Calibrate1():
    update1()
    bucket_1.corr1 = float(calWeight1.get())/(bucket_1.adcValue-bucket_1.tareValue)
    b1m.delete(0,END)
    b1m.insert(0, str(bucket_1.corr1))

def Calibrate2():
    update2()
    bucket_2.corr1 = float(calWeight2.get())/(bucket_2.adcValue-bucket_2.tareValue)
    b2m.delete(0,END)
    b2m.insert(0, str(bucket_2.corr1))

def calculateDensity(Grams,duration=20,area = 1):
    weightlbs = Grams*0.00220462
    gallons = weightlbs*0.11982844244
    density = gallons/area/duration
    return density

def calculateColor(weightGRAMS, duration = 20, area = 1, bucket=None):
    density = calculateDensity(weightGRAMS, duration, area)
    print "density = " + str(density)
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
    print color
    bucket.ledColor = color

b1read = Button(bottomframe, text="read data", bg="white", command=update1)
b1open = Button(bottomframe, text="open valve", bg="white", command= lambda: bucket_1.openValve(xbee))
b1close = Button(bottomframe, text="close valve", bg="white", command= lambda: bucket_1.closeValve(xbee))
b1setcolor = Button(bottomframe, text="set color", bg="white", command= lambda: bucket_1.setColor(bucket_1.adcValue))
b1m = Entry(bottomframe)
b1m.insert(0, bucket_1.corr1)
b1b = Entry(bottomframe)
b1b.insert(0, bucket_1.corr2)
b1tare = Button(bottomframe, text="tare",bg = "white", command = lambda: bucket_1.tare(xbee))
calWeight1 = Entry(bottomframe)
calWeight1.insert(0, "Enter Weight (grams)")
b1cal = Button(bottomframe, text="Calibrate", bg = "white", command = Calibrate1)

b2read = Button(bottomframe, text="read data", bg="white", command=update2)
b2open = Button(bottomframe, text="open valve", bg="white", command=lambda: bucket_2.openValve(xbee))
b2close = Button(bottomframe, text="close valve", bg="white", command=lambda: bucket_2.closeValve(xbee))
b2setcolor = Button(bottomframe, text="set color", bg="white", command=lambda: bucket_2.setColor(bucket_2.adcValue))
b2m = Entry(bottomframe)
b2m.insert(0,bucket_2.corr1)
b2b = Entry(bottomframe)
b2b.insert(0,bucket_2.corr2)
b2tare = Button(bottomframe, text="tare",bg = "white", command = lambda: bucket_2.tare(xbee))
calWeight2 = Entry(bottomframe)
calWeight2.insert(0, "Enter Weight (grams)")
b2cal = Button(bottomframe, text="Calibrate",bg="white", command = Calibrate2)

bucket1 = Label(b1frame, text="Bucket 1",bg = "white")
bucket2 = Label(b2frame, text="Bucket 2 ",bg = "white")

bucket1.grid(row=0,column=0,padx=15,pady=20)
bucket2.grid(row=0,column=1,padx=15,pady=20)

b1read.grid(row=1, column=0,padx=5,pady=5)
b1open.grid(row=2,column=0)
b1close.grid(row=3,column=0)
b1setcolor.grid(row=4,column=0)
b1m.grid(row=5,column=0)
b1b.grid(row=6,column=0)
b1tare.grid(row=7,column=0)
calWeight1.grid(row=8,column=0)
b1cal.grid(row=9,column=0)

b2read.grid(row=1, column=1,padx=5,pady=5)
b2open.grid(row=2,column=1)
b2close.grid(row=3,column=1)
b2setcolor.grid(row=4,column=1)
b2m.grid(row=5,column=1)
b2b.grid(row=6,column=1)
b2tare.grid(row=7,column=1)
calWeight2.grid(row=8,column=1)
b2cal.grid(row=9,column=1)

root.mainloop()

ser.close()