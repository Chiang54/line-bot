from fastapi import APIRouter, Query
from datetime import datetime, timedelta
import random
from lunardate import LunarDate
from routers.get_solar import get_solar_term

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
