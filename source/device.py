"""Device class.

This is the 'Device' class module for the f451 IoT Logger application and it 
manages the physical components of the IoT Logger device.
"""

import time
import board

import adafruit_touchscreen
from adafruit_pyportal import PyPortal

from display import Display as iotDspl
from display import Pixel as iotPxl
from display import ROT_LAND_RHT, VIEW_SPLASH

# =========================================================
#          G L O B A L S   A N D   H E L P E R S
# =========================================================
DEFAULT_NAME = "f541 IoT Logger"

BCKGRND_LOADING = "/images/f451-loading.bmp"

SOUND_DEMO = "/sounds/sound.wav"
SOUND_BEEP = "/sounds/beep.wav"
SOUND_TAB = "/sounds/tab.wav"

# =========================================================
#       C O M M O N   U T I L I T Y    C L A S S E S
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

    def init(self):
        pyportal = PyPortal()
        pyportal.set_background(BCKGRND_LOADING)  # Display an image until the loop starts

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
        self._pixel = iotPxl().init()

        self._display.set_background(0x000000)  # Display an image until the loop starts
        self._display.switch_view(VIEW_SPLASH)
        return self

    # def set_display(self, display):
    #     self._display = display

    # def set_touchscrn(self, touchscrn):
    #     self.touchscrn = touchscrn

    # def set_pixel(self, pixel):
    #     self._pixel = pixel

    def set_backlight(self, val):
        self._display.set_backlight(val)

    def set_rotation(self, rotation):
        self._display.set_rotation(rotation)

    # def show_main(self):
    #     self._display.set_background(BCKGRND_MAIN)

    def add_sensor(self, name, sensor=None):
        if name:
            self.sensors[name] = sensor

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

    def update_status(self, inStr):
        self._display.update_status(inStr)    

    def update_counter(self, inVal):
        self._display.update_counter(inVal)    

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
