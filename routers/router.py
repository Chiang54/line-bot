from fastapi import APIRouter, Query
from datetime import datetime
import random

router = APIRouter()

# ---- 模擬資料與工具函式 ----
ZODIAC_SIGNS = ['鼠', '牛', '虎', '兔', '龍', '蛇', '馬', '羊', '猴', '雞', '狗', '豬']
SUITABLE_ACTIVITIES = ['嫁娶', '出行', '交易', '開光', '祈福', '安床']
AVOID_ACTIVITIES = ['開市', '動土', '破土', '安葬', '入宅', '開倉']

def get_zodiac(year):
    return ZODIAC_SIGNS[(year - 4) % 12]

def mock_lunar_date(date_obj):
    lunar_month = (date_obj.month % 12) or 12
    lunar_day = (date_obj.day % 30) or 1
    return f"{lunar_month}月{lunar_day}日"

# ---- API 路由 ----
@router.get("/lunar")
async def get_lunar_info(date: str = Query(..., description="日期格式：YYYY-MM-DD")):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"error": "請提供正確的日期格式，例如：2025-01-01"}

    lunar_date = mock_lunar_date(date_obj)
    zodiac = get_zodiac(date_obj.year)
    weekday_str = f"星期{'一二三四五六日'[date_obj.weekday()]}"

    result = {
        "gregorian_date": date,
        "weekday": weekday_str,
        "lunar_date": lunar_date,
        "zodiac": zodiac,
        "suitable": random.sample(SUITABLE_ACTIVITIES, 3),
        "avoid": random.sample(AVOID_ACTIVITIES, 3)
    }
    return result
