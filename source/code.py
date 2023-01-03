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

---------------------------------------------------------------------------

Dependencies:
    * CircuitPython_AdafruitIO
        https://github.com/adafruit/Adafruit_CircuitPython_AdafruitIO
"""

import random
import time
import board
import busio

from device import BRIGHT_DEFAULT, Device as iotDev
from feed import Feed as iotFeed

import neopixel
from digitalio import DigitalInOut
from adafruit_io.adafruit_io import IO_HTTP
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
from adafruit_pyportal import PyPortal

# Get WiFi details and other 'secrets'
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in 'secrets.py', please add them there!")
    raise

# =========================================================
#          G L O B A L    V A R S   &   I N I T S
# =========================================================
DEVICE_NAME = "PyPortalTwo"
BCKGRND_LOADING = "/images/f451-loading.bmp"

FEED_NAME_TEMP = "temperature"
FEED_NAME_LIGHT = "light"

IO_DELAY = 30   # Timeout between sending data to Adafruit IO (in seconds)

STATUS_MSG = {
    "connect": "Connecting ...",
    "upload":  "Uploading data ...",
    "disconnect": "Disconnecting ...",
    "wait": "Waiting ...",
    "process": "Processing ...",
    "initWifi": "Initializing wifi ...",
    "initFeeds": "Initializing feeds ...",
    "error": "- ERROR -"
}

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
ADAFRUIT_IO_USER = secrets['aio_username']
ADAFRUIT_IO_KEY = secrets['aio_key']


# =========================================================
#              H E L P E R   F U N C T I O N S
# =========================================================
def _init_iot_feeds(io):
    feeds = {}
    feeds[FEED_NAME_TEMP] = iotFeed(FEED_NAME_TEMP).init(io)
    feeds[FEED_NAME_LIGHT] = iotFeed(FEED_NAME_LIGHT).init(io)
    return feeds


# =========================================================
#      C O R E   F U N C T I O N    /   A C T I O N S
# =========================================================
# PyPortal ESP32 Setup
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
statusPixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=BRIGHT_DEFAULT)

pyportal = PyPortal(esp=esp, external_spi=spi)
pyportal.set_background(BCKGRND_LOADING)  # Display an image until the loop starts

iotLogger = iotDev(DEVICE_NAME).init(pyportal=pyportal, pixel=statusPixel)

# Create an instance of the Adafruit IO HTTP client
iotLogger.update_status(STATUS_MSG["initWifi"])
wifiMgr = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, statusPixel)
ioHTTP = IO_HTTP(ADAFRUIT_IO_USER, ADAFRUIT_IO_KEY, wifiMgr)

iotLogger.update_status(STATUS_MSG["initFeeds"])
iotFeeds = _init_iot_feeds(ioHTTP)

# =========================================================
#                    M A I N   L O O P
# =========================================================
random.seed(1000)

loopFlg = True
# logStart = "Temperature: {}C\nLight data: {}Lumen".format(urandom(20, 30), urandom(1000, 9000))
# logDone = "Finished data upload.\nWaiting for {} sec until next loop.".format(FAKE_WAIT)

while True:
    counter = IO_DELAY
    iotLogger.update_counter(0)
    tempVal = iotLogger.sensor_get_temperature()
    lightVal = iotLogger.sensor_get_light_value()
    iotLogger.update_log("Temperature: {:.2f}°C\nLight data:  {:,} lum".format(tempVal, lightVal))

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
