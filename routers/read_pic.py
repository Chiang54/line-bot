import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from typing import List
import os

def preprocess_and_ocr(pil_image: Image.Image,fname) -> str:
    img = np.array(pil_image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 去彩色干擾點：只保留深色區域
    _, mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    gray = cv2.bitwise_and(gray, gray, mask=mask)

    # 中值濾波代替高斯，更適合濾雜訊點
    resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    blur = cv2.medianBlur(resized, 3)



    # 增強對比度
    adjusted = cv2.convertScaleAbs(blur, alpha=1.8, beta=-100)
    



    # 嘗試更大 blockSize + 更小 C
    thresh = cv2.adaptiveThreshold(
        adjusted, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 9
    )

    # 去小點（開運算）
    kernel = np.ones((1, 1), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)


    # 放大再辨識
    resized = cv2.resize(morph, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    # OCR
    config = "--psm 13 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    text = pytesseract.image_to_string(resized, config=config)

    return text.strip().replace(" ", "")
