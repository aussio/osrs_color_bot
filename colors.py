import numpy
import colorsys
import cv2

GREEN = numpy.array([100, 255, 0])
CYAN = numpy.array([0, 255, 255])
DARK_CYAN = numpy.array([0, 150, 255])
YELLOW = numpy.array([255, 255, 100])
MAGENTA = numpy.array([255, 0, 255])

BANK_TEXT_COLOR = numpy.array([255, 152, 31])
SOLID_GREEN = numpy.array([0, 255, 0])


def convert_rgb_to_hsv(rgb_color):
    # get hsv percentage: range (0-1, 0-1, 0-1)
    color_hsv_percentage = colorsys.rgb_to_hsv(*rgb_color)
    # get normal hsv: range (0-360, 0-255, 0-255)
    color_h = round(360 * color_hsv_percentage[0] / 2)
    color_s = round(255 * color_hsv_percentage[1])
    color_v = color_hsv_percentage[2]
    return (color_h, color_s, color_v)


def screenshot_to_hsv(image):
    temp_image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    return cv2.cvtColor(temp_image, cv2.COLOR_BGR2HSV)


def get_mask(image, color):
    hsv_color = numpy.array(convert_rgb_to_hsv(color))
    hsv_image = screenshot_to_hsv(image)
    return cv2.inRange(hsv_image, hsv_color, hsv_color)
