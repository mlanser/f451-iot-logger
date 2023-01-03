"""Display class.

This is the 'Display' class module for the f451 IoT Logger application and it 
manages the display components (i.e. physical screen, virtual display area, 
etc.) of the IoT Logger device.
"""

import time
import board
import displayio

from adafruit_button import Button
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_pyportal import PyPortal

from bitmap_font_forkawesome_icons import line_chart as ICON_CHART
from bitmap_font_forkawesome_icons import list_ as ICON_LOG
from bitmap_font_forkawesome_icons import pause as ICON_PAUSE
from bitmap_font_forkawesome_icons import play as ICON_RUN

# =========================================================
#          G L O B A L S   A N D   H E L P E R S
# =========================================================
FONT_HDR = "fonts/OpenSans-12.bdf"
FONT_DATA = "fonts/OpenSans-12.bdf"
FONT_STATUS = "fonts/OpenSans-12.bdf"
FONT_COUNTER = "fonts/OpenSans-Bold-16.bdf"
FONT_ICON = "fonts/forkawesome-42.pcf"

BCKGRND_SPLASH = "/images/f451-splash.bmp"
BCKGRND_MAIN = "/images/f451-splash.bmp"

# Hex Colors
COLOR_BLACK = 0x000000
COLOR_WHITE = 0xFFFFFF
COLOR_RED = 0xFF0000
COLOR_YELLOW = 0xFFFF00
COLOR_GREEN = 0x00FF00
COLOR_BLUE = 0x0000FF
COLOR_PURPLE = 0xFF00FF
COLOR_TURQUOISE = 0x00FFFF

ROT_LAND_RHT = 0    # Rotation 0 degrees: landscape - power right
ROT_PORT_TOP = 90   #     "   90    "     portrait  - power top
ROT_LAND_LFT = 180  #     "  180    "     landscape - power left
ROT_PORT_BTM = 270  #     "  270    "     portrait  - power bottom

STATE_PAUSE = 0     # 'Pause' logging 
STATE_RUN = 1       # 'Run'      "
STATE_LOG = 0       # 'Show log' view
STATE_CHART = 1     # 'Show chart' view

BTN_LBL_PAUSE = "PAUSE"
BTN_LBL_RUN = "RUN"
BTN_LBL_LOG = "LOG"
BTN_LBL_CHART = "CHART"

AREA_HDR_LBL = "SENSOR DATA"
AREA_LOG_LBL = "- Collecting data ... -"
AREA_CNTR_LBL = "{: >2} sec".format(0)
AREA_STATUS_LBL = "Processing ..."

AREA_HDR = "hdr"
AREA_STATUS = "status"
AREA_LOG = "log"
AREA_CHART = "chart"
AREA_CNTR = "counter"

VIEW_SPLASH = "splash"
VIEW_CHART = "chart"
VIEW_LOG = "log"

BTN_MODE = "mode"
BTN_VIEW = "view"

BTN_W = 76          # Button width
BTN_H = 76          # Button height
BTN_X = 3           # Button margin/distance 

AREA_X = 10
AREA_Y = 10

# =========================================================
#       C O M M O N   U T I L I T Y    C L A S S E S
# =========================================================
def _init_font_hdr():
    font = bitmap_font.load_font(FONT_HDR)
    font.load_glyphs(b"abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()")
    return font

def _init_font_main():
    font = bitmap_font.load_font(FONT_DATA)
    font.load_glyphs(b"abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()")
    return font

def _init_font_status():
    font = bitmap_font.load_font(FONT_STATUS)
    font.load_glyphs(b"abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()")
    return font

def _init_font_counter():
    font = bitmap_font.load_font(FONT_COUNTER)
    font.load_glyphs(b"abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()")
    return font

def _init_font_icon():
    font = bitmap_font.load_font(FONT_ICON)
    return font


# =========================================================
#       C O R E   C L A S S   D E F I N I T I O N S
# =========================================================
class Display(object):
    """IoT Logger display class.

    This class manages the (virtual) display component that
    handles buttons, text areas, backgrounds, etc.
    """

    def __init__(self, pyportal):
        self.id = board.board_id
        self._display = board.DISPLAY
        self._device = pyportal
        self.state = None
        self.width = 0
        self.height = 0
        self.rotation = 0
        self.backlight = 0
        self.font = None
        self.views = {}
        self.buttons = {}
        self.areas = {}

    def init(self):
        self._state = State()
        self.font = _init_font_main()
        self.rotation = ROT_LAND_RHT

        self.height = self._init_height(ROT_LAND_RHT)
        self.width = self._init_width(ROT_LAND_RHT)
        self.backlight = self._init_backlight()

        self.views[VIEW_SPLASH] = _init_splash(BCKGRND_SPLASH)      # The Main Display Group
        self.views[VIEW_CHART] = _init_chart_view()                 # Group for CHART VIEW objects
        self.views[VIEW_LOG] = _init_log_view()                     # Group for LOG VIEW objects

        self.buttons[BTN_MODE] = {
            "btn": _make_mode_btn(self.width, self.height, self.font, BTN_LBL_PAUSE), 
            "state": True
        }
        self.buttons[BTN_VIEW] = {
            "btn": _make_view_btn(self.width, self.height, self.font, BTN_LBL_CHART), 
            "state": False
        }

        self.areas[AREA_CNTR] = {
            "area": _make_cntr_area(self.width, self.height, _init_font_counter(), AREA_CNTR_LBL),
            "state": True
        }
        self.areas[AREA_STATUS] = {
            "area": _make_status_area(self.height, _init_font_status(), AREA_STATUS_LBL),
            "state": True
        }
        self.areas[AREA_HDR] = {
            "area": _make_hdr_area(_init_font_hdr(), AREA_HDR_LBL),
            "state": True
        }
        self.areas[AREA_LOG] = {
            "area": _make_log_area(_init_font_main(), AREA_LOG_LBL),
            "state": True
        }

        self.views[VIEW_SPLASH].append(self.buttons[BTN_VIEW]["btn"])
        self.views[VIEW_SPLASH].append(self.buttons[BTN_MODE]["btn"])
        self.views[VIEW_SPLASH].append(self.areas[AREA_CNTR]["area"])
        self.views[VIEW_SPLASH].append(self.areas[AREA_HDR]["area"])
        self.views[VIEW_SPLASH].append(self.areas[AREA_STATUS]["area"])

        self.views[VIEW_LOG].append(self.areas[AREA_LOG]["area"])

        self.select_run_mode()
        self.select_log_view()

        return self

    # return a reformatted string with word wrapping using PyPortal.wrap_nicely
    def _wrap_area_text(self, areaName, inStr, maxChars=30):
        tmpText = inStr.split("\n")
        outText = ""
        test = ""

        for seg in tmpText:
            tmp = self._device.wrap_nicely(seg, maxChars)
            for w in tmp:
                outText += "\n" + w
                test += "M\n"

        txtHeight = Label(self.font, text="M", color=COLOR_TURQUOISE)
        txtHeight.text = test                               # Odd things happen without this
        self.areas[areaName]["area"].text = ""              # Odd things happen without this
        self.areas[areaName]["area"].text = outText

    def _init_width(self, rotation=ROT_LAND_RHT):
        # If landscape mode 
        if rotation == ROT_LAND_RHT or rotation == ROT_LAND_LFT:
            return 480 if self.id == "pyportal_titano" else 320

        # If portrait mode
        else:
            return 320 if self.id == "pyportal_titano" else 240

    def _init_height(self, rotation=ROT_LAND_RHT):
        # If landscape mode 
        if rotation == ROT_LAND_RHT or rotation == ROT_LAND_LFT:
            return 320 if self.id == "pyportal_titano" else 240

        # If portrait mode
        else:
            return 480 if self.id == "pyportal_titano" else 320

    def _init_backlight(self):
        # 0.3 brightness is not enought to make Titatno display visible
        return 1 if self.id == "pyportal_titano" else 0.5

    # def _add_buttons(self, name, arrBbuttons):
    #     self.buttons[name] = arrBbuttons

    # def _add_view(self, name, view):
    #     self.views[name] = view

    def select_run_mode(self):
        self.buttons[BTN_MODE]["btn"].label = BTN_LBL_PAUSE
        self.buttons[BTN_MODE]["btn"].selected = True
        self.buttons[BTN_MODE]["state"] = True
        return self

    def select_pause_mode(self):
        self.buttons[BTN_MODE]["btn"].label = BTN_LBL_RUN
        self.buttons[BTN_MODE]["btn"].selected = False
        self.buttons[BTN_MODE]["state"] = False
        return self

    def select_chart_view(self):
        self.buttons[BTN_VIEW]["btn"].label = BTN_LBL_LOG
        self.buttons[BTN_VIEW]["btn"].selected = True
        self.buttons[BTN_VIEW]["state"] = True
        self.switch_view(self.views[VIEW_CHART])
        return self

    def select_log_view(self, inStr=""):
        self.buttons[BTN_VIEW]["btn"].label = BTN_LBL_CHART
        self.buttons[BTN_VIEW]["btn"].selected = False
        self.buttons[BTN_VIEW]["state"] = False
        self._wrap_area_text(AREA_LOG, inStr)
        _hide_layer(self.views[VIEW_SPLASH], self.views[VIEW_CHART])
        _show_layer(self.views[VIEW_SPLASH], self.views[VIEW_LOG])
        return self

    def switch_view(self, view):
        self._display.show(self.views[view])

    def set_rotation(self, rotation=0):
        self._display.rotation = rotation
    
    def set_background(self, inVal):
        self._device.set_background(inVal)
    
    def play_sound(self, fnAudio=""):
        if fnAudio:
            self._device.play_file(fnAudio)

    def set_backlight(self, val):
         # Value can be 0 to 1, where 0 is OFF, 0.5 is 50%,
         # and 1 is 100% brightness.
        val = max(0, min(1.0, val))
        try:
            self._display.auto_brightness = False
        except AttributeError:
            pass

        self._display.brightness = val
        return self

    def update_log(self, inStr):
        prntStr = str(inStr)[0:90]              # We want max 90 chars

        if self.areas[AREA_LOG]["state"]:       # Is 'counter' area active?
            self._wrap_area_text(AREA_LOG, prntStr)

        return self

    def update_status(self, inStr):
        prntStr = str(inStr)[0:30]              # We want max 30 chars

        if self.areas[AREA_STATUS]["state"]:       # Is 'counter' area active?
            self.areas[AREA_STATUS]["area"].text = prntStr

        return self

    def update_counter(self, inVal):
        prntVal = int(inVal) % 100              # We want max 2 digits!
        if self.areas[AREA_CNTR]["state"]:      # Is 'counter' area active?
            self.areas[AREA_CNTR]["area"].text = "{: >2} sec".format(prntVal)

        return self

    def self_test(self):
        print("Display Dims:   {}px(W) x {}px(H)".format(self.width, self.height))
        print(" - Rotation:    {} degrees".format(self.rotation))
        print(" - Backlight:   {}".format(self.backlight))
        print(" - Groups:      {}".format(len(self.views)))
        for nm in self.views.keys():
            print("   - {}".format(nm))
        self._state.self_test()    


class State(object):
    """IoT Logger device state class.

    This class manages the state of the display. In other words,
    it keeps track of which view is displayed, what state 'switch'
    buttons (e.g. 'start' or 'stop') are in, etc.
    """
    def __init__(self):
        self.view = None
        self.btnPauseRun = STATE_RUN
        self.btnChartLog = STATE_LOG

    def self_test(self):
        print("Btn 'ChartLog': {}".format(BTN_LBL_LOG if self.btnChartLog == STATE_LOG else BTN_LBL_CHART))
        print("Btn 'PauseRun': {}".format(BTN_LBL_RUN if self.btnPauseRun == STATE_RUN else BTN_LBL_PAUSE))



# =========================================================
#              U T I L I T Y   F U N C T I O N S
# =========================================================
# Set visibility of layer
def _hide_layer(layer, target):
    try:
        layer.remove(target)
    except ValueError:
        pass


def _show_layer(layer, target):
    try:
        time.sleep(0.1)
        layer.append(target)
    except ValueError:
        pass


def _init_splash(fName):
    grpSplash = displayio.Group()
    grpBckgrnd = displayio.Group()
    grpSplash.append(grpBckgrnd)

    # _set_image(grpBckgrnd, fName)

    return grpSplash


def _init_chart_view():
    grpChart= displayio.Group()
    return grpChart


def _init_log_view():
    grpLog = displayio.Group()
    return grpLog


def _set_image(group, fName):
    """Assign image to a given group.

    Use this for setting/swapping icons, background images, etc.
        :param group: group to assign image to
        :param fName: path for image
    """
    # print("Set image to ", fName)
    if group:
        group.pop()

    if not fName:
        return  # Exit of no valid filename

    # CircuitPython 7+ compatible
    image = displayio.OnDiskBitmap(fName)
    group.append(displayio.TileGrid(image, pixel_shader=image.pixel_shader))


def _make_view_btn(scrnW, scrnH, font, btnLbl):
    return Button(
        x=scrnW - BTN_W - BTN_X,
        y=BTN_X,
        width=BTN_W,
        height=BTN_H,
        label=btnLbl,
        label_font=font,
        label_color=COLOR_TURQUOISE,
        fill_color=COLOR_BLACK,
        outline_color=COLOR_TURQUOISE,
        selected_fill=COLOR_BLACK,
        selected_outline=COLOR_TURQUOISE,
        selected_label=COLOR_TURQUOISE,
    )


def _make_mode_btn(scrnW, scrnH, font, btnLbl):
    return Button(
        x=scrnW - BTN_W - BTN_X,
        y=(2 * BTN_X) + BTN_H,
        width=BTN_W,
        height=BTN_H,
        label=btnLbl,
        label_font=font,
        label_color=COLOR_TURQUOISE,
        fill_color=COLOR_BLACK,
        outline_color=COLOR_TURQUOISE,
        selected_fill=COLOR_BLACK,
        selected_outline=COLOR_TURQUOISE,
        selected_label=COLOR_TURQUOISE,
    )


def _make_status_area(scrnH, font, areaLbl):
    area = Label(font, text=areaLbl , color=COLOR_TURQUOISE)
    area.x = AREA_X
    area.y = scrnH - int(BTN_H / 2)
    return area


def _make_cntr_area(scrnW, scrnH, font, areaLbl):
    area = Label(font, text=areaLbl , color=COLOR_TURQUOISE)
    area.x = scrnW - BTN_W
    area.y = scrnH - int(BTN_H / 2)
    return area


def _make_hdr_area(font, areaLbl):
    area = Label(font, text=areaLbl , color=COLOR_TURQUOISE)
    area.x = AREA_X
    area.y = AREA_Y
    return area


def _make_log_area(font, areaLbl):
    area = Label(font, text=areaLbl , color=COLOR_TURQUOISE)
    area.x = AREA_X
    area.y = AREA_Y * 3
    return area
