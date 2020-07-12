# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 09:44:34 2020

@author: PAVA
"""


import serial
ser = serial.Serial('/dev/ttyACM0')
ser.flushInput()

while True:
    try:
        ser_bytes = ser.readline()
        decoded_bytes = float(ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
        print(decoded_bytes)
    except:
        print("Keyboard Interrupt")
        break
    