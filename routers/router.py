from fastapi import APIRouter, Query
from datetime import datetime
import random
from lunardate import LunarDate
from routers.get_solar import get_solar_longitude

router = APIRouter()

@router.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


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

@router.get("/lunar")
async def get_lunar_info(date: str = Query(..., description="西元日期，格式為 YYYY-MM-DD")):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"error": "請提供正確的日期格式，例如：2025-01-01"}

    lunar = LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
    lunar_date_str = format_lunar_date(lunar.month, lunar.day)
    zodiac = get_zodiac(lunar.year)
    weekday_str = f"星期{'一二三四五六日'[date_obj.weekday()]}"
    solar_term = get_solar_term_from_date(date_obj)

    return {
        "gregorian_date": date,
        "weekday": weekday_str,
        "lunar_date": lunar_date_str,
        "zodiac": zodiac,
        "solar_term": solar_term or "無",
        "suitable": random.sample(SUITABLE_ACTIVITIES, 3),
        "avoid": random.sample(AVOID_ACTIVITIES, 3)
    }
