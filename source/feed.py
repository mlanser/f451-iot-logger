"""Feed class.

This is the 'Feed' class module for the f451 IoT Logger application and it 
manages the attributes for  agiven Adafruit IO feed.

Dependencies:
    * CircuitPython_AdafruitIO
        https://github.com/adafruit/Adafruit_CircuitPython_AdafruitIO
"""

from adafruit_io.adafruit_io import AdafruitIO_RequestError

# =========================================================
#          G L O B A L S   A N D   H E L P E R S
# =========================================================



# =========================================================
#       C O M M O N   U T I L I T Y    C L A S S E S
# =========================================================


# =========================================================
#       C O R E   C L A S S   D E F I N I T I O N S
# =========================================================
class Feed(object):
    """IoT Logger feed class.

    This class manages the attributes of an Adafruit IO feed.
    """

    def __init__(self, feedName):
        self._name = feedName
        self._feed = None

    def init(self, io):
        try:
            # Get feed if it exists ...
            self.feed = io.get_feed(self._name)
        except AdafruitIO_RequestError:
            # ... or crete it as needed
            self.feed = io.create_new_feed(self._name)

        return self


# =========================================================
#              U T I L I T Y   F U N C T I O N S
# =========================================================
