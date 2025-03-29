from fastapi import APIRouter, Query
from datetime import datetime
import random
from lunardate import LunarDate


router = APIRouter()

@router.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


# 農民曆查詢(參數[date=2025-01-01])
ZODIAC_SIGNS = ['鼠', '牛', '虎', '兔', '龍', '蛇', '馬', '羊', '猴', '雞', '狗', '豬']
SUITABLE_ACTIVITIES = ['嫁娶', '出行', '交易', '開光', '祈福', '安床']
AVOID_ACTIVITIES = ['開市', '動土', '破土', '安葬', '入宅', '開倉']

def get_zodiac(year):
    return ZODIAC_SIGNS[(year - 4) % 12]

@router.get("/lunar")
async def get_lunar_info(date: str = Query(..., description="西元日期，格式為 YYYY-MM-DD")):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"error": "請提供正確的日期格式，例如：2025-01-01"}

    lunar = LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
    lunar_date_str = f"{lunar.month}月{lunar.day}日"
    zodiac = get_zodiac(lunar.year)
    weekday_str = f"星期{'一二三四五六日'[date_obj.weekday()]}"

    return {
        "gregorian_date": date,
        "weekday": weekday_str,
        "lunar_date": lunar_date_str,
        "zodiac": zodiac,
        "suitable": random.sample(SUITABLE_ACTIVITIES, 3),
        "avoid": random.sample(AVOID_ACTIVITIES, 3)
    }
