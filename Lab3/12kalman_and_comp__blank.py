#!/usr/bin/python
#    This program  reads the angles from the acceleromter, gyrscope
#    and mangnetometeron a BerryIMU connected to a Raspberry Pi.
#
#    This program includes a number of calculations to improve the 
#    values returned from BerryIMU. If this is new to you, it 
#    may be worthwhile first to look at berryIMU-simple.py, which 
#    has a much more simplified version of code which would be easier
#    to read.   
#
#    http://ozzmaker.com/
#
#    Copyright (C) 2016  Mark Williams
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Library General Public
#    License as published by the Free Software Foundation; either
#    version 2 of the License, or (at your option) any later version.
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    Library General Public License for more details.
#    You should have received a copy of the GNU Library General Public
#    License along with this library; if not, write to the Free
#    Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
#    MA 02111-1307, USA


import Adafruit_ADXL345
import string
import sys, os, math, time, thread, smbus, random, requests
import Queue
from signal import signal, SIGPIPE, SIG_DFL
import smbus
import time
import math
import datetime
bus = smbus.SMBus(1)

RAD_TO_DEG = 57.29578
M_PI = math.pi
G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40      # Complementary filter constant

#Kalman filter variables
Q_angle = 0.02
Q_gyro = 0.0015
R_angle = 0.005
y_bias = 0.0
x_bias = 0.0
XP_00 = 0.0
XP_01 = 0.0
XP_10 = 0.0
XP_11 = 0.0
YP_00 = 0.0
YP_01 = 0.0
YP_10 = 0.0
YP_11 = 0.0
KFangleX = 0.0
KFangleY = 0.0



def kalmanFilterY ( accAngle, gyroRate, DT):
    y=0.0
    S=0.0

    global KFangleY
    global Q_angle
    global Q_gyro
    global y_bias
    global YP_00
    global YP_01
    global YP_10
    global YP_11

    KFangleY = KFangleY + DT * (gyroRate - y_bias)

    YP_00 = YP_00 + ( - DT * (YP_10 + YP_01) + Q_angle * DT )
    YP_01 = YP_01 + ( - DT * YP_11 )
    YP_10 = YP_10 + ( - DT * YP_11 )
    YP_11 = YP_11 + ( + Q_gyro * DT )

    y = accAngle - KFangleY
    S = YP_00 + R_angle
    K_0 = YP_00 / S
    K_1 = YP_10 / S
    
    KFangleY = KFangleY + ( K_0 * y )
    y_bias = y_bias + ( K_1 * y )
    
    YP_00 = YP_00 - ( K_0 * YP_00 )
    YP_01 = YP_01 - ( K_0 * YP_01 )
    YP_10 = YP_10 - ( K_1 * YP_00 )
    YP_11 = YP_11 - ( K_1 * YP_01 )
    
    return KFangleY

def kalmanFilterX ( accAngle, gyroRate, DT):
    x=0.0
    S=0.0

    global KFangleX
    global Q_angle
    global Q_gyro
    global x_bias
    global XP_00
    global XP_01
    global XP_10
    global XP_11


    KFangleX = KFangleX + DT * (gyroRate - x_bias)

    XP_00 = XP_00 + ( - DT * (XP_10 + XP_01) + Q_angle * DT )
    XP_01 = XP_01 + ( - DT * XP_11 )
    XP_10 = XP_10 + ( - DT * XP_11 )
    XP_11 = XP_11 + ( + Q_gyro * DT )

    x = accAngle - KFangleX
    S = XP_00 + R_angle
    K_0 = XP_00 / S
    K_1 = XP_10 / S
    
    KFangleX = KFangleX + ( K_0 * x )
    x_bias = x_bias + ( K_1 * x )
    
    XP_00 = XP_00 - ( K_0 * XP_00 )
    XP_01 = XP_01 - ( K_0 * XP_01 )
    XP_10 = XP_10 - ( K_1 * XP_00 )
    XP_11 = XP_11 - ( K_1 * XP_01 )
    
    return KFangleX

def getSignedNumber(number):
    if number & (1 << 15):
        return number | ~65535
    else:
        return number & 65535

def read_word(address, adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr + 1)
    val = (high << 8) + low
    return val

def read_word_2c(address, adr):
    val = read_word(address, adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0
kalmanX = 0.0
kalmanY = 0.0

a = datetime.datetime.now()

# =============== sensor setting ===============
# put your code
accel = Adafruit_ADXL345.ADXL345()

i2c_bus=smbus.SMBus(1)
i2c_address=0x69
i2c_bus.write_byte_data(i2c_address,0x20,0x0F)
i2c_bus.write_byte_data(i2c_address,0x23,0x20)

bus = smbus.SMBus(1)
addrHMC = 0x1e
bus.write_byte_data(addrHMC, 0, 0b01110000)  # Set to 8 samples @ 15Hz
bus.write_byte_data(addrHMC, 1, 0b00100000)  # 1.3 gain LSb / Gauss 1090 (default)
bus.write_byte_data(addrHMC, 2, 0b00000000)  # Continuous sampling
# =============== sensor setting ===============

while True:
    
    # ================= Read the accelerometer,gyroscope and magnetometer values =================
    x, y, z = accel.read()
    ACCx = x / 256.0
    ACCy = y / 256.0
    ACCz = z / 256.0

    i2c_bus.write_byte(i2c_address,0x28)
    X_L = i2c_bus.read_byte(i2c_address)
    i2c_bus.write_byte(i2c_address,0x29)
    X_H = i2c_bus.read_byte(i2c_address)
    X = X_H << 8 | X_L

    i2c_bus.write_byte(i2c_address,0x2A)
    Y_L = i2c_bus.read_byte(i2c_address)
    i2c_bus.write_byte(i2c_address,0x2B)
    Y_H = i2c_bus.read_byte(i2c_address)
    Y = Y_H << 8 | Y_L

    i2c_bus.write_byte(i2c_address,0x2C)
    Z_L = i2c_bus.read_byte(i2c_address)
    i2c_bus.write_byte(i2c_address,0x2D)
    Z_H = i2c_bus.read_byte(i2c_address)
    Z = Z_H << 8 | Z_L

    GYRx = getSignedNumber(X)
    GYRy = getSignedNumber(Y)
    GYRz = getSignedNumber(Z)

    MAGx = float(read_word_2c(addrHMC, 3)) * 0.92
    MAGy = float(read_word_2c(addrHMC, 7)) * 0.92
    MAGz = float(read_word_2c(addrHMC, 5)) * 0.92
	# ================= Read the accelerometer,gyroscope and magnetometer values =================

    
    ##Calculate delay (Loop Period, LP). How long between Gyro Reads
    b = datetime.datetime.now() - a
    a = datetime.datetime.now()
    LP = b.microseconds/(1000000*1.0)
    #print "Loop Time | %5.2f|" % ( LP ),
    
    
    #Convert Gyro raw to degrees per second
    rate_gyr_x =  GYRx * G_GAIN
    rate_gyr_y =  GYRy * G_GAIN
    rate_gyr_z =  GYRz * G_GAIN


    #Calculate the angles from the gyro. 
    gyroXangle+=rate_gyr_x*LP
    gyroYangle+=rate_gyr_y*LP
    gyroZangle+=rate_gyr_z*LP


    ##Convert Accelerometer values to degrees
    AccXangle =  (math.atan2(ACCy,ACCz)+M_PI)*RAD_TO_DEG
    AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG
    
    
    ####################################################################
    ######################Correct rotation value########################
    ####################################################################
    #Change the rotation value of the accelerometer to -/+ 180 and
        #move the Y axis '0' point to up.
        #
        #Two different pieces of code are used depending on how your IMU is mounted.
    #If IMU is up the correct way, Skull logo is facing down, Use these lines
    AccXangle -= 180.0
    if AccYangle > 90:
        AccYangle -= 270.0
    else:
        AccYangle += 90.0
    #
    #
    #
    #
    #If IMU is upside down E.g Skull logo is facing up;
    #if AccXangle >180:
        #        AccXangle -= 360.0
    #AccYangle-=90
    #if (AccYangle >180):
        #        AccYangle -= 360.0
    ############################ END ##################################


    #Complementary filter used to combine the accelerometer and gyro values.
    CFangleX=AA*(CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
    CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle
    
    #Kalman filter used to combine the accelerometer and gyro values.
    kalmanY = kalmanFilterY(AccYangle, rate_gyr_y,LP)
    kalmanX = kalmanFilterX(AccXangle, rate_gyr_x,LP)
       
    #Calculate heading
    heading = 180 * math.atan2(MAGy,MAGx)/M_PI

    #Only have our heading between 0 and 360
    if heading < 0:
         heading += 360

    #Normalize accelerometer raw values.
    accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
    accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
    
    ####################################################################
    ###################Calculate pitch and roll#########################
    ####################################################################
    #Use these two lines when the IMU is up the right way. Skull logo is facing down
    pitch = math.asin(accXnorm)
    roll = -math.asin(accYnorm/math.cos(pitch))
    #
    #Us these four lines when the IMU is upside down. Skull logo is facing up
    #accXnorm = -accXnorm                #flip Xnorm as the IMU is upside down
    #accYnorm = -accYnorm                #flip Ynorm as the IMU is upside down
    #pitch = math.asin(accXnorm)
    #roll = math.asin(accYnorm/math.cos(pitch))
    #
    ############################ END ##################################

    #Calculate the new tilt compensated values
    magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
    magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)

    #Calculate tilt compensated heading
    tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI

    if tiltCompensatedHeading < 0:
        tiltCompensatedHeading += 360


    if 1:            #Change to '0' to stop showing the angles from the accelerometer
        print ("%5.2f \t %5.2f \t" % (AccXangle, AccYangle)),
    if 1:            #Change to '0' to stop  showing the angles from the gyro
        print ("%5.2f \t %5.2f \t %5.2f \t" % (gyroXangle,gyroYangle,gyroZangle)),
    if 1:            #Change to '0' to stop  showing the angles from the complementary filter
        print ("%5.2f \t %5.2f \t" % (CFangleX,CFangleY)),
    if 1:            #Change to '0' to stop  showing the angles from the Kalman filter
        print ("%5.2f \t %5.2f" % (kalmanX,kalmanY))
#    if 1:            #Change to '0' to stop  showing the heading
#        print ("HEADING %5.2f, tiltCompensatedHeading %5.2f;" % (heading,tiltCompensatedHeading)),
		
    #slow program down a bit, makes the output more readable
    time.sleep(0.03)