"""Device class.

This is the 'Device' class module for the f451 IoT Logger application and it 
manages the physical components of the IoT Logger device.
"""

import random
import time
import board
import neopixel

import adafruit_touchscreen
from adafruit_pyportal import PyPortal

from display import ROT_LAND_RHT, VIEW_SPLASH, Display as iotDspl
from sensor import LightSensor, TempSensor

# =========================================================
#          G L O B A L S   A N D   H E L P E R S
# =========================================================
DEFAULT_NAME = "f541 IoT Logger"

SNSR_NAME_TEMP = "temperature"
SNSR_NAME_LIGHT = "light"

SOUND_DEMO = "/sounds/sound.wav"
SOUND_BEEP = "/sounds/beep.wav"
SOUND_TAB = "/sounds/tab.wav"

BRIGHT_MIN = 0          # Brightness of the pixel(s) between 0.0 and 
BRIGHT_MAX = 1          # 1.0 where 1.0 is full brightness
BRIGHT_DEFAULT = 0.2    # Default brightness


# =========================================================
#              H E L P E R   F U N C T I O N S
# =========================================================


# =========================================================
#       C O R E   C L A S S   D E F I N I T I O N S
# =========================================================
class Device(object):
    """IoT Logger device class.

    This class manages the (physical) components (e.g. touchscreen, 
    display, sensors, etc.) of the device.
    """
    def __init__(self, nickname=""):
        self.name = DEFAULT_NAME
        self.nickname = nickname
        self._display = None
        self._touchscrn = None
        self._pixel = None
        self.sensors = {}

    def init(self, pyportal=None, pixel=None):
        if not pyportal:
            pyportal = PyPortal()
        self._display = iotDspl(pyportal).init()
        self._display.set_backlight(self._display.backlight)
        self._display.set_rotation(ROT_LAND_RHT)

        self._touchscrn = adafruit_touchscreen.Touchscreen(
            board.TOUCH_YD,
            board.TOUCH_YU,
            board.TOUCH_XR,
            board.TOUCH_XL,
            calibration=((5200, 59000), (5800, 57000)),
            size=(self._display.width, self._display.height),
        )

        if not pixel:
            pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=BRIGHT_DEFAULT)
        self._pixel = pixel

        self.sensors[SNSR_NAME_TEMP] = TempSensor(SNSR_NAME_TEMP)
        self.sensors[SNSR_NAME_LIGHT] = LightSensor(SNSR_NAME_LIGHT)

        self._display.set_background(0x000000)  # Display an image until the loop starts
        self._display.switch_view(VIEW_SPLASH)
        return self

    def set_backlight(self, val):
        self._display.set_backlight(val)
        return self

    def set_rotation(self, rotation):
        self._display.set_rotation(rotation)
        return self

    def play_demo(self):
        self._display.play_sound(SOUND_DEMO)

    def play_beep(self):
        self._display.play_sound(SOUND_BEEP)

    def play_tab(self):
        self._display.play_sound(SOUND_TAB)

    def show_log(self, inStr=""):
        self._display.select_log_view(inStr)

    def update_log(self, inStr):
        self._display.update_log(inStr)    
        return self

    def update_status(self, inStr):
        self._display.update_status(inStr)    
        return self

    def update_counter(self, inVal):
        self._display.update_counter(inVal)    
        return self

    def sensor_get_temperature(self):
        return self.sensors[SNSR_NAME_TEMP].get_value()
        # return random.randrange(20, 30)

    def sensor_get_light_value(self):
        return self.sensors[SNSR_NAME_LIGHT].get_value()
        # return random.randrange(1000, 9000)

    def self_test(self):
        print("Device Name:    {}".format(self.name))
        if self.nickname:
            print(" - Nickname:    {}".format(self.nickname))

        self._display.self_test()

        print("Touchscreen:    {}".format("enabled" if self._touchscrn else "disabled"))
        print("Pixel:          {}".format("enabled" if self._pixel else "disabled"))
        print("Sensors:        {}".format("enabled" if self.sensors else "disabled"))


# =========================================================
#              U T I L I T Y   F U N C T I O N S
# =========================================================
