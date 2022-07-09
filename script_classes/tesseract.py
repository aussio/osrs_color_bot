import cv2
import pytesseract
import numpy as np

from copy import copy


def bw_processing(img):
    """Turn image to black text on white background. Return original too."""
    # Keep light colors, but turn the rest black.
    light_text_only = cv2.threshold(img, 250, 255, cv2.THRESH_BINARY)[1]

    # Invert to be white background with black remaining
    black_mask = np.all(light_text_only == [0, 0, 0], axis=-1)
    non_black = np.any(light_text_only != [0, 0, 0], axis=-1)
    light_text_only[black_mask] = [255, 255, 255]
    light_text_only[non_black] = [0, 0, 0]

    return light_text_only


def image_to_string(img, psm="--psm 6"):
    return pytesseract.image_to_string(img, config=f"{psm} digits -c tessedit_char_whitelist=+0123456789").strip()


def img_to_str_bw_processing(img):
    bw_image = bw_processing(img)

    zoom_factor = 2
    zoom_img = copy(bw_image)
    zoom_img = cv2.resize(bw_image, (bw_image.shape[1] * zoom_factor, bw_image.shape[0] * zoom_factor))
    blur_img = copy(zoom_img)
    blur_img = cv2.medianBlur(blur_img, ksize=5)

    print(pytesseract.get_tesseract_version())

    return image_to_string(blur_img)
