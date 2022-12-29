# SPDX-FileCopyrightText: 2020 Richard Albritton for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import board
import microcontroller
import displayio
import busio
from analogio import AnalogIn
import neopixel
import adafruit_adt7410
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_button import Button
import adafruit_touchscreen
from adafruit_pyportal import PyPortal

# ------------- Constants ------------- #
# Sound Effects
SOUND_DEMO = "/sounds/sound.wav"
SOUND_BEEP = "/sounds/beep.wav"
SOUND_TAB = "/sounds/tab.wav"

# Hex Colors
COLOR_WHITE = 0xFFFFFF
COLOR_RED = 0xFF0000
COLOR_YELLOW = 0xFFFF00
COLOR_GREEN = 0x00FF00
COLOR_BLUE = 0x0000FF
COLOR_PURPLE = 0xFF00FF
COLOR_BLACK = 0x000000

# Default Label styling
TABS_X = 0
TABS_Y = 15

# Default button styling:
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 80

# Default state
gAppState = {
    'view': 1,      # Global VIEW state
    'icon': 1,      # Global ICON state
    'btnMode': 1,   # Global BUTTON mode
    'swState': 0    # Global SWITCH state
}

# ------------- Functions ------------- #
# Backlight function
def set_backlight(val):
    try:
        board.DISPLAY.auto_brightness = False
    except AttributeError:
        pass

    # Value between 0 and 1 where 0 is OFF, 0.5 is 50% and 1 is 100% brightness.
    board.DISPLAY.brightness = max(0, min(1.0, val))


# Helper for cycling through a number set of 1 to x.
def numberUP(num, max_val):
    return (num % max_val) + 1


# Set visibility of layer
def show_layer(layer, target):
    try:
        time.sleep(0.1)
        layer.append(target)
    except ValueError:
        pass

def hide_layer(layer, target):
    try:
        layer.remove(target)
    except ValueError:
        pass


# This will handle switching Images and Icons
def set_image(group, filename):
    """Set the image file for a given goup for display.
    This is most useful for Icons or image slideshows.
        :param group: The chosen group
        :param filename: The filename of the chosen image
    """
    print("Set image to ", filename)
    if group:
        group.pop()

    if not filename:
        return  # we're done, no icon desired

    # CircuitPython 6 & 7 compatible
    # image_file = open(filename, "rb")
    # image = displayio.OnDiskBitmap(image_file)
    # image_sprite = displayio.TileGrid(
    #     image, pixel_shader=getattr(image, "pixel_shader", displayio.ColorConverter())
    # )

    # # CircuitPython 7+ compatible
    image = displayio.OnDiskBitmap(filename)
    image_sprite = displayio.TileGrid(image, pixel_shader=image.pixel_shader)

    group.append(image_sprite)


# return a reformatted string with word wrapping using PyPortal.wrap_nicely
def text_box(target, top, string, max_chars):
    text = pyportal.wrap_nicely(string, max_chars)
    new_text = ""
    test = ""

    for w in text:
        new_text += "\n" + w
        test += "M\n"

    text_height = Label(font, text="M", color=0x03AD31)
    text_height.text = test  # Odd things happen without this
    glyph_box = text_height.bounding_box
    target.text = ""  # Odd things happen without this
    target.y = int(glyph_box[3] / 2) + top
    target.text = new_text


def get_Temperature(source):
    if source:  # Only if we have the temperature sensor
        celsius = source.temperature
    else:  # No temperature sensor
        celsius = microcontroller.cpu.temperature
    return (celsius * 1.8) + 32


# =====================================
# Core processes
# -------------------------------------
def process_touch(inTouch, inBtns, inPortal, inTouchScrn, inPixel, inIconGroup, inSwitchBtn, inState):
    outFlg = False
    outState = inState

    if inTouch:                                 # Did user touch screen?
                                                # If yes, loop over buttons using enumerate()
        for i, btn in enumerate(inBtns):
            if btn.contains(inTouch):           # Test each button to see if it was pressed
                print("button{} pressed".format(i))

                if i == 0 and inState['view'] != 1:      # only if view1 is visible
                    inPortal.play_file(SOUND_TAB)
                    switch_view(1)
                    while inTouchScrn.touch_point:
                        pass

                if i == 1 and inState['view'] != 2:      # only if view2 is visible
                    inPortal.play_file(SOUND_TAB)
                    switch_view(2)
                    while inTouchScrn.touch_point:
                        pass

                if i == 2 and inState['view'] != 3:      # only if view3 is visible
                    inPortal.play_file(SOUND_TAB)
                    switch_view(3)
                    while inTouchScrn.touch_point:
                        pass

                if i == 3:
                    inPortal.play_file(SOUND_BEEP)
                    # Toggle switch button type
                    if inState['swState'] == 0:
                        outState['swState'] = 1
                        btn.label = "ON"
                        btn.selected = False
                        inPixel.fill(COLOR_WHITE)
                        print("Switch ON")
                    else:
                        outState['swState'] = 0
                        btn.label = "OFF"
                        btn.selected = True
                        inPixel.fill(COLOR_BLACK)
                        print("Switch OFF")
                    # for debounce
                    while inTouchScrn.touch_point:
                        pass
                    print("Switch Pressed")

                if i == 4:
                    inPortal.play_file(SOUND_BEEP)
                    # Momentary button type
                    btn.selected = True
                    print("Button Pressed")
                    outState['btnMode'] = numberUP(inState['btnMode'], 5)

                    if outState['btnMode'] == 1:
                        inPixel.fill(COLOR_RED)
                    elif outState['btnMode'] == 2:
                        inPixel.fill(COLOR_YELLOW)
                    elif outState['btnMode'] == 3:
                        inPixel.fill(COLOR_GREEN)
                    elif outState['btnMode'] == 4:
                        inPixel.fill(COLOR_BLUE)
                    elif outState['btnMode'] == 5:
                        inPixel.fill(COLOR_PURPLE)

                    outState['swState'] = 1
                    inSwitchBtn.label = "ON"
                    inSwitchBtn.selected = False

                    # for debounce
                    while inTouchScrn.touch_point:
                        pass

                    print("Button released")
                    btn.selected = False

                if i == 5 and inState['view'] == 2:  # only if view2 is visible
                    inPortal.play_file(SOUND_BEEP)
                    btn.selected = True
                    while inTouchScrn.touch_point:
                        pass
                    print("Icon Button Pressed")
                    outState['icon'] = numberUP(inState['icon'], 3)
                    if outState['icon'] == 1:
                        iconName = "Ruby"
                    elif outState['icon'] == 2:
                        iconName = "Gus"
                    elif outState['icon'] == 3:
                        iconName = "Billie"
                    btn.selected = False
                    text_box(
                        feed2_label,
                        TABS_Y,
                        "Every time you tap the Icon button the icon image will "
                        "change. Say hi to {}!".format(iconName),
                        18,
                    )
                    set_image(inIconGroup, "/images/" + iconName + ".bmp")

                if i == 6 and inState['view'] == 3:  # only if view3 is visible
                    btn.selected = True
                    while inTouchScrn.touch_point:
                        pass
                    print("Sound Button Pressed")
                    inPortal.play_file(SOUND_DEMO)
                    btn.selected = False
    
    return outFlg, outState


# =====================================
# Init system components
# -------------------------------------
# Init PyPortal and pixel
pyportal = PyPortal()
pyportal.set_background("/images/loading.bmp")  # Display an image until the loop starts
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=1)

# -------------------------------------
# Touchscreen setup  [ Rotate 270 ]
display = board.DISPLAY
display.rotation = 270

if board.board_id == "pyportal_titano":
    screen_width = 320
    screen_height = 480
    set_backlight(1)        # 0.3 brightness does not make display visible on Titano
else:
    screen_width = 240
    screen_height = 320
    set_backlight(0.3)

# -------------------------------------
# Init touchscreen area
touchScrn = adafruit_touchscreen.Touchscreen(
    board.TOUCH_YD,
    board.TOUCH_YU,
    board.TOUCH_XR,
    board.TOUCH_XL,
    calibration=((5200, 59000), (5800, 57000)),
    size=(screen_width, screen_height),
)

# -------------------------------------
# Init sensors
light_sensor = AnalogIn(board.LIGHT)
try:
    # attempt to init. the temperature sensor
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    adt = adafruit_adt7410.ADT7410(i2c_bus, address=0x48)
    adt.high_resolution = True
except ValueError:
    # Did not find ADT7410. Probably running on Titano or Pynt
    adt = None




# ------------- Screen Setup ------------- #

# We want three buttons across the top of the screen
TAB_BUTTON_Y = 0
TAB_BUTTON_HEIGHT = 40
TAB_BUTTON_WIDTH = int(screen_width / 3)

# We want two big buttons at the bottom of the screen
BIG_BUTTON_HEIGHT = int(screen_height / 3.2)
BIG_BUTTON_WIDTH = int(screen_width / 2)
BIG_BUTTON_Y = int(screen_height - BIG_BUTTON_HEIGHT)

# ------------- Display Groups ------------- #
splash = displayio.Group()      # Main display group
view1 = displayio.Group()       # Group for View 1 objects
view2 = displayio.Group()       # Group for View 2 objects
view3 = displayio.Group()       # Group for View 3 objects

# ------------- Setup for Images ------------- #
bg_group = displayio.Group()
splash.append(bg_group)
set_image(bg_group, "/images/BGimage.bmp")

iconGroup = displayio.Group()
iconGroup.x = 180
iconGroup.y = 120
iconGroup.scale = 1
view2.append(iconGroup)

# ---------- Text Boxes ------------- #
# Set the font and preload letters
font = bitmap_font.load_font("/fonts/Helvetica-Bold-16.bdf")
font.load_glyphs(b"abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()")

# Text Label Objects
feed1_label = Label(font, text="Text Window 1", color=0xE39300)
feed1_label.x = TABS_X
feed1_label.y = TABS_Y
view1.append(feed1_label)

feed2_label = Label(font, text="Text Window 2", color=0xFFFFFF)
feed2_label.x = TABS_X
feed2_label.y = TABS_Y
view2.append(feed2_label)

sensors_label = Label(font, text="Data View", color=0x03AD31)
sensors_label.x = TABS_X
sensors_label.y = TABS_Y
view3.append(sensors_label)

sensor_data = Label(font, text="Data View", color=0x03AD31)
sensor_data.x = TABS_X + 16  # Indents the text layout
sensor_data.y = 150
view3.append(sensor_data)

# ---------- Display Buttons ------------- #
# This group will make it easy for us to read a button press later.
buttons = []

# Main User Interface Buttons
btnView1 = Button(
    x=0,  # Start at furthest left
    y=0,  # Start at top
    width=TAB_BUTTON_WIDTH,  # Calculated width
    height=TAB_BUTTON_HEIGHT,  # Static height
    label="View 1",
    label_font=font,
    label_color=0xFF7E00,
    fill_color=0x5C5B5C,
    outline_color=0x767676,
    selected_fill=0x1A1A1A,
    selected_outline=0x2E2E2E,
    selected_label=0x525252,
)
buttons.append(btnView1)  # adding this button to the buttons group

btnView2 = Button(
    x=TAB_BUTTON_WIDTH,  # Start after width of a button
    y=0,
    width=TAB_BUTTON_WIDTH,
    height=TAB_BUTTON_HEIGHT,
    label="View 2",
    label_font=font,
    label_color=0xFF7E00,
    fill_color=0x5C5B5C,
    outline_color=0x767676,
    selected_fill=0x1A1A1A,
    selected_outline=0x2E2E2E,
    selected_label=0x525252,
)
buttons.append(btnView2)  # adding this button to the buttons group

btnView3 = Button(
    x=TAB_BUTTON_WIDTH * 2,  # Start after width of 2 buttons
    y=0,
    width=TAB_BUTTON_WIDTH,
    height=TAB_BUTTON_HEIGHT,
    label="View 3",
    label_font=font,
    label_color=0xFF7E00,
    fill_color=0x5C5B5C,
    outline_color=0x767676,
    selected_fill=0x1A1A1A,
    selected_outline=0x2E2E2E,
    selected_label=0x525252,
)
buttons.append(btnView3)  # adding this button to the buttons group

btnOnOff = Button(
    x=0,  # Start at furthest left
    y=BIG_BUTTON_Y,
    width=BIG_BUTTON_WIDTH,
    height=BIG_BUTTON_HEIGHT,
    label="Light Switch",
    label_font=font,
    label_color=0xFF7E00,
    fill_color=0x5C5B5C,
    outline_color=0x767676,
    selected_fill=0x1A1A1A,
    selected_outline=0x2E2E2E,
    selected_label=0x525252,
)
buttons.append(btnOnOff)  # adding this button to the buttons group

btnLightColor = Button(
    x=BIG_BUTTON_WIDTH,  # Starts just after button 1 width
    y=BIG_BUTTON_Y,
    width=BIG_BUTTON_WIDTH,
    height=BIG_BUTTON_HEIGHT,
    label="Light Color",
    label_font=font,
    label_color=0xFF7E00,
    fill_color=0x5C5B5C,
    outline_color=0x767676,
    selected_fill=0x1A1A1A,
    selected_outline=0x2E2E2E,
    selected_label=0x525252,
)
buttons.append(btnLightColor)  # adding this button to the buttons group

# Add all of the main buttons to the splash Group
for btn in buttons:
    splash.append(btn)

# Make a button to change the icon image on view2
btnIcon = Button(
    x=150,
    y=60,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="Icon",
    label_font=font,
    label_color=0xFFFFFF,
    fill_color=0x8900FF,
    outline_color=0xBC55FD,
    selected_fill=0x5A5A5A,
    selected_outline=0xFF6600,
    selected_label=0x525252,
    style=Button.ROUNDRECT,
)
buttons.append(btnIcon)  # adding this button to the buttons group

# Add this button to view2 Group
view2.append(btnIcon)

# Make a button to play a sound on view2
btnSound = Button(
    x=150,
    y=170,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="Sound",
    label_font=font,
    label_color=0xFFFFFF,
    fill_color=0x8900FF,
    outline_color=0xBC55FD,
    selected_fill=0x5A5A5A,
    selected_outline=0xFF6600,
    selected_label=0x525252,
    style=Button.ROUNDRECT,
)
buttons.append(btnSound)  # adding this button to the buttons group

# Add this button to view2 Group
view3.append(btnSound)

# pylint: disable=global-statement
def switch_view(inView):
    global gAppState

    if inView == 1:
        btnView1.selected = False
        btnView2.selected = True
        btnView3.selected = True
        hide_layer(splash, view2)
        hide_layer(splash, view3)
        show_layer(splash, view1)
    elif inView == 2:
        # global icon
        btnView1.selected = True
        btnView2.selected = False
        btnView3.selected = True
        hide_layer(splash, view1)
        hide_layer(splash, view3)
        show_layer(splash, view2)
    else:
        btnView1.selected = True
        btnView2.selected = True
        btnView3.selected = False
        hide_layer(splash, view1)
        hide_layer(splash, view2)
        show_layer(splash, view3)

    # Set global button state
    gAppState['view'] = inView
    print("View {view_num:.0f} On".format(view_num=inView))


# pylint: enable=global-statement

# Set veriables and startup states
btnView1.selected = False
btnView2.selected = True
btnView3.selected = True
btnOnOff.label = "OFF"
btnOnOff.selected = True

show_layer(splash, view1)
hide_layer(splash, view2)
hide_layer(splash, view3)

# Update out Labels with display text.
text_box(
    feed1_label,
    TABS_Y,
    "The text on this screen is wrapped so that all of it fits nicely into a "
    "text box that is {} x {}.".format(
        feed1_label.bounding_box[2], feed1_label.bounding_box[3] * 2
    ),
    30,
)

text_box(feed2_label, TABS_Y, "Tap on the Icon button to meet a new friend.", 18)

text_box(
    sensors_label,
    TABS_Y,
    "This screen can display sensor readings and tap Sound to play a WAV file.",
    28,
)


# =====================================
# Initialize UI
# -------------------------------------
board.DISPLAY.show(splash)


# =====================================
# Main loop
# -------------------------------------
loopFlg = True

while loopFlg:
    touch = touchScrn.touch_point
    light = light_sensor.value
    sensor_data.text = "Touch: {}\nLight: {}\nTemp: {:.0f}°F".format(
        touch, light, get_Temperature(adt)
    )

    # Adjust backlight
    # Will also cause screen to dim when hand is blocking sensor to touch screen
    if light < 1500:
        set_backlight(0.1)
    elif light < 3000:
        set_backlight(0.5)
    else:
        set_backlight(1)

    # ------------- Handle Button Press Detection  ------------- #
    skipFlg, gAppState = process_touch(touch, buttons, pyportal, touchScrn, pixel, iconGroup, btnOnOff, gAppState)
