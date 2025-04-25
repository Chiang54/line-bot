from fastapi import APIRouter, Query, FastAPI, UploadFile, File
from datetime import datetime, timedelta
import random
from lunardate import LunarDate
from routers.get_solar import get_solar_term
from PIL import Image
import pytesseract
from io import BytesIO
import cv2
import numpy as np


router = APIRouter()

@router.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@router.post("/ocr")
async def ocr(image: UploadFile = File(...)):
    image_bytes = await image.read()
    image_stream = BytesIO(image_bytes)
    image_obj = Image.open(image_stream)

    text = preprocess_and_ocr(image_obj)
    return {"text": text.strip()}

def preprocess_and_ocr(pil_image: Image.Image) -> str:
    import cv2
    import numpy as np
    from PIL import Image
    import pytesseract

    # 轉成 OpenCV 可處理的格式
    img = np.array(pil_image.convert("RGB"))

    # 轉灰階
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 加強對比：自動直方圖均衡化
    gray = cv2.equalizeHist(gray)

    # 去噪：高斯模糊
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # 二值化（自適應門檻效果通常比固定值更好）
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 6
    )

    # 去雜訊（開運算）
    kernel = np.ones((2, 2), np.uint8)
    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # DEBUG：存下處理後圖片（可選）
    # cv2.imwrite("cleaned.png", clean)

    # OCR：用 psm 7（單列文字），也可以試試 6 或 8
    text = pytesseract.image_to_string(clean, config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

    return text.strip()


# 農民曆查詢(參數[date=2025-01-01])
ZODIAC_SIGNS = ['鼠', '牛', '虎', '兔', '龍', '蛇', '馬', '羊', '猴', '雞', '狗', '豬']
SUITABLE_ACTIVITIES = ['嫁娶', '出行', '交易', '開光', '祈福', '安床']
AVOID_ACTIVITIES = ['開市', '動土', '破土', '安葬', '入宅', '開倉']

LUNAR_MONTHS = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '臘月']
LUNAR_DAYS = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十', '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十', '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']

def get_zodiac(year):
    return ZODIAC_SIGNS[(year - 4) % 12]

def format_lunar_date(month: int, day: int) -> str:
    month_str = LUNAR_MONTHS[month - 1]
    day_str = LUNAR_DAYS[day - 1]
    return f"{month_str}{day_str}"

@router.get("/lunar_day")
async def get_lunarday_info(date: str = Query(..., description="西元日期，格式為 YYYY-MM-DD")):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"error": "請提供正確的日期格式，例如：2025-01-01"}

    lunar = LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
    lunar_date_str = format_lunar_date(lunar.month, lunar.day)
    zodiac = get_zodiac(lunar.year)
    weekday_str = f"星期{'一二三四五六日'[date_obj.weekday()]}"
    solar_term = get_solar_term(date_obj)

    return {
        "gregorian_date": date,
        "weekday": weekday_str,
        "lunar_date": lunar_date_str,
        "zodiac": zodiac,
        "solar_term": solar_term or "",
        "suitable": random.sample(SUITABLE_ACTIVITIES, 3),
        "avoid": random.sample(AVOID_ACTIVITIES, 3)
    }


@router.get("/lunar_month")
async def get_lunar_month_info(
    year: int = Query(..., description="西元年，例如：2025"),
    month: int = Query(..., description="月份，1~12")
):
    try:
        start_date = datetime(year, month, 1)
    except ValueError:
        return {"error": "請提供正確的年月格式，例如：2025 年 1 月"}

    # 計算當月天數
    next_month = start_date.replace(day=28) + timedelta(days=4)
    end_date = next_month.replace(day=1) - timedelta(days=1)

    result = []
    current_date = start_date
    while current_date <= end_date:
        lunar = LunarDate.fromSolarDate(current_date.year, current_date.month, current_date.day)
        lunar_date_str = format_lunar_date(lunar.month, lunar.day)
        zodiac = get_zodiac(lunar.year)
        weekday_str = f"星期{'一二三四五六日'[current_date.weekday()]}"
        solar_term = get_solar_term(current_date)

        result.append({
            "gregorian_date": current_date.strftime("%Y-%m-%d"),
            "weekday": weekday_str,
            "lunar_date": lunar_date_str,
            "zodiac": zodiac,
            "solar_term": solar_term or "",
            "suitable": random.sample(SUITABLE_ACTIVITIES, 3),
            "avoid": random.sample(AVOID_ACTIVITIES, 3)
        })
        current_date += timedelta(days=1)

    return result


# 假設以下函式與常數已定義：
# format_lunar_date(month, day)
# get_zodiac(year)
# get_solar_term(date_obj)
# SUITABLE_ACTIVITIES, AVOID_ACTIVITIES

@router.get("/lunar_year")
async def get_lunar_year_info(
    year: int = Query(..., description="西元年，例如：2025")
):
    try:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
    except ValueError:
        return {"error": "請提供正確的年份，例如：2025"}

    result = []
    current_date = start_date
    while current_date <= end_date:
        lunar = LunarDate.fromSolarDate(current_date.year, current_date.month, current_date.day)
        lunar_date_str = format_lunar_date(lunar.month, lunar.day)
        zodiac = get_zodiac(lunar.year)
        weekday_str = f"星期{'一二三四五六日'[current_date.weekday()]}"
        solar_term = get_solar_term(current_date)

        result.append({
            "gregorian_date": current_date.strftime("%Y-%m-%d"),
            "weekday": weekday_str,
            "lunar_date": lunar_date_str,
            "zodiac": zodiac,
            "solar_term": solar_term or "",
            "suitable": random.sample(SUITABLE_ACTIVITIES, 3),
            "avoid": random.sample(AVOID_ACTIVITIES, 3)
        })
        current_date += timedelta(days=1)

    return result
