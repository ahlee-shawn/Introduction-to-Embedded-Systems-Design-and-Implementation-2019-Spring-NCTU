import RPi.GPIO as GPIO
import smbus
import socket
import threading
from adxl345 import ADXL345
import os
import sys 
import time
import numpy as np
import math
Gear = 38
Calibrate = 15
Terminate = 40
Flap_Button_Up = 7
Flap_Button_Down = 12
Speed_Up = 11
Speed_Down = 13
i = 0
gear = 1
current_flap = 0
benchmark = np.zeros((3), dtype=np.float32)
benchmark_acc = np.zeros((3), dtype=np.float32)
maxDirectionAcce = np.zeros((4,3), dtype=np.float32)
direction = ["\nshift to right","\nshift to up","\nshift to down", "\nmodify done"]
plat = np.zeros((3), dtype=np.float32)
platSqrt = 1.0
directX = np.zeros((3), dtype=np.float32)
directY = np.zeros((3), dtype=np.float32)
current = np.zeros((3), dtype=np.float32)

def GEAR(channel):
    global gear
    gear = int(gear == 0)

def ADD_FLAP(channel):
    global current_flap
    if current_flap < 5:
        current_flap += 1

def MINUS_FLAP(channel):
    global current_flap
    if current_flap > 0:
        current_flap -= 1

def CALIBRATE(channel):
    global benchmark,benchmark_acc
    benchmark = np.zeros((3), dtype=np.float32)
    benchmark_acc = np.zeros((3), dtype=np.float32)
    for i in range(0, 100):
        a, b ,c = get_gyro()
        benchmark += np.array([a,b,c])
    benchmark /= 100
    print(benchmark)
    temp = [0.0, 0.0, 0.0]
    for i in range(0, 100):
        axes = adxl345.getAxes(True)
        benchmark_acc += np.array([axes['x'],axes['y'],axes['z']])
    benchmark_acc /= 100
    print(benchmark_acc)

def TERMINATE(channel):
    global maxDirectionAcce, plat, directX, directY, i ,benchmark_acc
    #terminate = 1
    os.system('clear')
    print(direction[i])
    axes = adxl345.getAxes(True)
    maxDirectionAcce[i] = (np.array([axes['x'],axes['y'],axes['z']]) - benchmark_acc )*100
    #maxDirectionAcce[i][0] = (axes['x'] - benchmark_acc_x) * 100
    #maxDirectionAcce[i][1] = (axes['y'] - benchmark_acc_y) * 100
    #maxDirectionAcce[i][2] = (axes['z'] - benchmark_acc_z) * 100
    #maxDirectionAcce[i] = (axes -
    #[benchmark_acc_x,benchmark_acc_y,benchmark_acc_z])*100
    #maxDirectionAcce = np.array(        [[15.0,-11.0,-42.0],        [-5.0,-11.0, 31.0],        [74.0, 53.0, 10.0],        [13.0,-114.0, 5.0]])
    if i == 3:
        directX = (maxDirectionAcce[1] - maxDirectionAcce[0])#/np.linalg.norm((maxDirectionAcce[1] - maxDirectionAcce[0]))
        directY = (maxDirectionAcce[3] - maxDirectionAcce[2])#/np.linalg.norm((maxDirectionAcce[3] - maxDirectionAcce[2]))
            #directYy = sqrt(directY[0]**+directY[1]**+directY[2]**)
        plat = np.cross(directX,directY)
        plat/=np.linalg.norm(plat)
        time.sleep(3)
        i+=1
    elif i == 4:
        os.system('clear')
        print("\nPress button 2 to scale 4 directions\n")
        i = 0
    else:
        i += 1


GPIO.setmode(GPIO.BOARD)
GPIO.setup(Gear, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Gear, GPIO.FALLING, callback=GEAR, bouncetime=250)
GPIO.setup(Flap_Button_Up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Flap_Button_Up, GPIO.FALLING, callback=ADD_FLAP, bouncetime=250)
GPIO.setup(Flap_Button_Down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Flap_Button_Down, GPIO.FALLING, callback=MINUS_FLAP, bouncetime=250)
GPIO.setup(Calibrate, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Calibrate, GPIO.FALLING, callback=CALIBRATE, bouncetime=250)
GPIO.setup(Terminate, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Terminate, GPIO.FALLING, callback=TERMINATE, bouncetime=250)
GPIO.setup(Speed_Up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Speed_Down, GPIO.IN, pull_up_down=GPIO.PUD_UP)



def getSignedNumber(number):
    if int(number) & (1 << 15):
        return int(number) | ~65535
    else:
        return int(number) & 65535

def get_gyro():
    #global X, Y, Z
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

    X = getSignedNumber(X) * 70 / 1000
    Y = getSignedNumber(Y) * 70 / 1000
    Z = getSignedNumber(Z) * 70 / 1000
    return X, Y, Z

class Client(object):   
    def __init__(self, ip, port):
        try:
            #socket.inet_aton(ip)
            if 0 < int(port) < 65535:
                self.ip = ip
                self.port = int(port)
            else:
                raise Exception('Port value should between 1~65535')
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(1)
  
    def run(self):
        global current, plat, platSqrt, directX, directY ,benchmark_acc , benchmark
        j = 0
        while True:
            j += 1
            start = time.time()
            x, y, z = np.array(get_gyro()) - benchmark
            #x, y, z = np.array([10.0,10.0,10.0]) - benchmark
            #x -= benchmark_x
            #y -= benchmark_y
            #z -= benchmark_z
            calibrate = int(GPIO.input(Calibrate) == GPIO.LOW)
            add_speed = int(GPIO.input(Speed_Up) == GPIO.LOW)
            minus_speed = int(GPIO.input(Speed_Down) == GPIO.LOW)
            #if abs(x) < 3 : x = 0;
            #if abs(y) < 3 : y = 0;
            #if abs(z) < 3 : z = 0;
            current += 0.1*np.array([x,y,z]) 
            #current_x += (x * 0.1)
            #current_y += (y * 0.1)
            #current_z += (z * 0.1)
            #sign should be sloved
            axes = adxl345.getAxes(True)
            #acc_x = axes['x'] - benchmark_acc_x
            #acc_y = axes['y'] - benchmark_acc_y
            #acc_z = axes['z'] - benchmark_acc_z
            acc_x, acc_y, acc_z = np.array([axes['x'],axes['y'],axes['z']])- benchmark_acc
            projection = np.array([acc_x,acc_y,acc_z])-plat*(np.dot(np.array([acc_x,acc_y,acc_z]),plat))
            print(projection[0:2])
            matriX = np.vstack((directX, directY))[:, :-1]
            print(np.shape(projection))
            rangeS = np.dot(np.array(projection[0:2]),np.linalg.pinv(matriX))
            #print(rangeS.shape)
            y = -50 * rangeS[0]
            z = -90 * rangeS[1]
            if(j>=7):
                current[1] = 100*y
                current[2] = 100*z
                j = 0 
            
            os.system('clear')
            #os.system('clr')
            print("Gear: {}".format(gear))
            print("calibrate: {}".format(calibrate))
            print("terminate: {}".format(0))
            print("add_speed: {}".format(add_speed))
            print("minus_speed: {}".format(minus_speed))
            print("flap: {}".format(current_flap))
            print("current_x: {}".format(current[0]))
            print("current_y: {}".format(current[1]))
            print("current_z: {}".format(current[2]))
            print("x: {}".format(0))
            print("y: {}".format(100*y))
            print("z: {}".format(100*z))
            print("acc_x: {:.2f}".format(acc_x))
            print("acc_y: {:.2f}".format(acc_y))
            print("acc_z: {:.2f}".format(acc_z))
            #msg = format(int(gear), '01b') + format(int(calibrate), '01b') + format(int(terminate), '01b') + format(int(add_speed), '01b') + format(int(minus_speed), '01b') + format(int(current_flap), '03b') + format(int(sign_x), '01b') + format(int(x), '013b') + format(int(sign_y), '01b') + format(int(y), '013b') + format(int(sign_z), '01b') + format(int(z), '013b')
            #msg = format(int(gear), '01b') + format(int(calibrate), '01b') + "0" + format(int(add_speed), '01b')+ format(int(minus_speed), '01b') + format(int(current_flap), '03b') + format(int(x), '013b') + format(int(y), '013b') + format(int(z), '013b')
            msg = format(int(gear), '01b') + format(int(calibrate), '01b') + "0" + format(int(add_speed), '01b')+ format(int(minus_speed), '01b') + format(int(current_flap), '03b') + format(int(0), '013b') + format(int(10*current[1]), '018b') + format(int(10*current[2]), '018b')
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.port))
                s.send(msg.encode())
            time_past = time.time() - start
            time_to_sleep = 0.1 - time_past
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)
            #else:
                #print(time_to_sleep)
def launch_client(ip, port):
    global i
    c = Client(ip, port)
    print("\nCalibrate first\n")
    print("Press button 2 to scale 4 directions\n")
    print("shift to left\n")
    while True:
        if i > 3:
            c.run()
        else :
            time.sleep(0.1)
            

if __name__ == "__main__":
    i2c_bus = smbus.SMBus(1)
    i2c_address = 0x69
    i2c_bus.write_byte_data(i2c_address,0x20,0x0F)
    i2c_bus.write_byte_data(i2c_address,0x23,0x20)
    adxl345 = ADXL345()
    
    if len(sys.argv) == 3:
        launch_client(sys.argv[1], sys.argv[2])
    else:
        print('Usage: python3 {} IP PORT'.format(sys.argv[0]))