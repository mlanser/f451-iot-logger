"""Sensor class.

This is the 'Sensor' class module for the f451 IoT Logger application and it 
manages the attributes for a (hardware) given sensor.

Dependencies:
    * CircuitPython_ADT7410
        https://github.com/adafruit/Adafruit_CircuitPython_ADT7410
"""

import board
import busio
from analogio import AnalogIn
import adafruit_adt7410

# =========================================================
#          G L O B A L S   A N D   H E L P E R S
# =========================================================
TEMP_C = "c"        # Celsius
TEMP_F = "F"        # Fahrenheit


# =========================================================
#       C O M M O N   U T I L I T Y    C L A S S E S
# =========================================================


# =========================================================
#       C O R E   C L A S S   D E F I N I T I O N S
# =========================================================
class Sensor(object):
    """IoT Logger sensor class.

    This class manages the attributes of a (hardware) sensor.
    """

    def __init__(self, snsrName):
        self._name = snsrName
        self._status = True

    def get_value(self):
        pass

    def enable(self):
        self._status = True

    def disable(self):
        self._status = False

    @property
    def status(self):
        return self._status     

class LightSensor(Sensor):
    """IoT Logger Light Sensor class.

    This class manages the attributes of the light sensor.
    """

    def __init__(self, snsrName):
        super().__init__(snsrName)

        # Set up analog light sensor on PyPortal
        self._sensor = AnalogIn(board.LIGHT)

    def get_value(self):
        return self._sensor.value


class TempSensor(Sensor):
    """IoT Logger Temperature Sensor class.

    This class manages the attributes of the temperature sensor.
    """

    def __init__(self, snsrName):
        super().__init__(snsrName)

        # Set up ADT7410 sensor
        i2cBus = busio.I2C(board.SCL, board.SDA)
        self._sensor = adafruit_adt7410.ADT7410(i2cBus, address=0x48)
        self._sensor.high_resolution = True

    def get_value(self, unit=TEMP_C):
        celsius = self._sensor.temperature
        return celsius if unit == TEMP_C else (celsius * 1.8) + 32
