import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from typing import List
import os

# 1. Generate templates A-Z, 0-9
CHAR_SET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
TEMPLATE_SIZE = (20, 30)

try:
    TEMPLATE_FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
except OSError:
    TEMPLATE_FONT = ImageFont.load_default()

def generate_templates() -> dict:
    templates = {}
    for char in CHAR_SET:
        img = Image.new('L', TEMPLATE_SIZE, color=255)
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), char, font=TEMPLATE_FONT)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((TEMPLATE_SIZE[0]-w)/2, (TEMPLATE_SIZE[1]-h)/2), char, font=TEMPLATE_FONT, fill=0)
        templates[char] = np.array(img)
    return templates

# 2. Split CAPTCHA image into 4 character sub-images

def split_characters(image: np.ndarray, count: int = 4) -> List[np.ndarray]:
    h, w = image.shape[:2]
    step = w // count
    chars = [image[0:h, i*step:(i+1)*step] for i in range(count)]
    return chars

# 3. Match single character using template

def match_character(char_img: np.ndarray, templates: dict) -> str:
    max_score = -1
    matched_char = ''
    for char, tmpl in templates.items():
        resized = cv2.resize(char_img, TEMPLATE_SIZE)
        res = cv2.matchTemplate(resized, tmpl, cv2.TM_CCOEFF_NORMED)
        score = res[0][0]
        if score > max_score:
            max_score = score
            matched_char = char
    return matched_char

# 4. Full recognition pipeline using template matching

def preprocess_and_ocr(pil_image: Image.Image) -> str:
    # Convert to OpenCV format
    img = np.array(pil_image.convert("RGB"))

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Equalize histogram
    gray = cv2.equalizeHist(gray)

    # Denoise with Gaussian blur
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 6
    )

    # Morphological open operation to remove noise
    kernel = np.ones((2, 2), np.uint8)
    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Split and match using template
    templates = generate_templates()
    chars = split_characters(clean)
    result = ''.join([match_character(c, templates) for c in chars])

    return result