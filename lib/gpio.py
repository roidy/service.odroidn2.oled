import time

def initGPIO():
    try:
        with open("/sys/class/gpio/export", "w") as fp:
            fp.write("477")
    except:
        pass

    try:
        with open("/sys/class/gpio/export", "w") as fp:
            fp.write("476")
    except:
        pass

    try:
        with open("/sys/class/gpio/gpio477/direction", "w") as fp:
            fp.write("out")
    except:
        pass

    try:
        with open("/sys/class/gpio/gpio476/direction", "w") as fp:
            fp.write("out")
    except:
        pass

def gpioWriteDC(val):
    try:
        with open("/sys/class/gpio/gpio477/value", "w") as fp:
            fp.write(str(val))
    except:
        pass

def gpioWriteReset(val):
    try:
        with open("/sys/class/gpio/gpio476/value", "w") as fp:
            fp.write(str(val))
    except:
        pass

def gpioDoReset():
    gpioWriteReset(1)
    time.sleep(0.1)
    gpioWriteReset(0)
    time.sleep(0.1)
    gpioWriteReset(1)
    time.sleep(0.1)
