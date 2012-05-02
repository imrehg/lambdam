from time import sleep
from random import gauss, shuffle
from socketIO import SocketIO
s = SocketIO('localhost', 5000)

numchn = 6
vals = [350.0 for i in range(numchn)]

while True:
    try:
        order = range(numchn)
        shuffle(order)
        for i in order:
            vals[i] += gauss(0, 0.1)
            out = {"wavelength" : { "channel": i+1, "value": vals[i]}}
            print out
            s.emit('message', out)
            sleep(0.05)
    except (KeyboardInterrupt):
        print("Stopping")
        break
