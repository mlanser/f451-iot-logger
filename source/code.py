"""f451 IoT Logger.

This is the main module for the f451 IoT Logger application. The objective 
for this module is to initialize system components and run the main loop.

(c) 2023 Martin Lanser
License: MIT

---------------------------------------------------------------------------

This application is based on concepts and ideas outlined in various Adafruit 
tutorials. Adafruit is the main sponsor for CircuitPython and invests time 
and resources providing tutorials and more.

Please support Adafruit and open source hardware by purchasing
products from Adafruit!

All text above must be included in any redistribution.
"""

# from os import urandom as random
import random
import time
from device import Device as iotDev

# =========================================================
#          G L O B A L    V A R S   &   I N I T S
# =========================================================
DEVICE_NAME = "PyPortalTwo"

STATUS_MSG = {
    "connect": "Connecting ...",
    "upload":  "Uploading data ...",
    "disconnect": "Disconnecting ...",
    "wait": "Waiting ...",
    "process": "Processing ...",
    "error": "- ERROR -",
}

iotLogger = iotDev(DEVICE_NAME).init()

# =========================================================
#              H E L P E R   F U N C T I O N S
# =========================================================


# =========================================================
#      C O R E   F U N C T I O N    /   A C T I O N S
# =========================================================


# =========================================================
#                    M A I N   L O O P
# =========================================================
FAKE_WAIT = 15
random.seed(1000)

loopFlg = True
# logStart = "Temperature: {}C\nLight data: {}Lumen".format(urandom(20, 30), urandom(1000, 9000))
# logDone = "Finished data upload.\nWaiting for {} sec until next loop.".format(FAKE_WAIT)

while True:
    counter = FAKE_WAIT
    iotLogger.update_counter(0)
    iotLogger.update_log("Temperature: {:.2f} C\nLight data:  {:,} lum".format(random.randrange(20, 30), random.randrange(1000, 9000)))

    iotLogger.update_status(STATUS_MSG["connect"])
    time.sleep(1)

    iotLogger.update_status(STATUS_MSG["upload"])
    time.sleep(2)

    iotLogger.update_status(STATUS_MSG["disconnect"])
    time.sleep(1)

    iotLogger.update_status(STATUS_MSG["wait"])

    while counter >= 0:
        iotLogger.update_counter(counter)
        counter -= 1
        # iotLogger.self_test()
        time.sleep(1)
        # loopFlg = False
        # pass
