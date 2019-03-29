import sys, os, math, time, thread, smbus, random, requests

bus = smbus.SMBus(1)
addrHMC = 0x1e

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

def main():

    bus.write_byte_data(addrHMC, 0, 0b01110000)  # Set to 8 samples @ 15Hz
    bus.write_byte_data(addrHMC, 1, 0b00100000)  # 1.3 gain LSb / Gauss 1090 (default)
    bus.write_byte_data(addrHMC, 2, 0b00000000)  # Continuous sampling

    while True:
        x = float(read_word_2c(addrHMC, 3)) * 0.92
        y = float(read_word_2c(addrHMC, 7)) * 0.92
        z = float(read_word_2c(addrHMC, 5)) * 0.92

        print math.degrees(math.atan2(y, x)),",",x,",",y
        time.sleep(0.1)

if __name__ == "__main__":
    main()