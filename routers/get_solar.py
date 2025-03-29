import math
from datetime import datetime, timedelta

# 建立簡化的節氣推算演算法（黃經法）
# 資料來源：近似太陽視黃經計算（精度約±1日），用於辨別節氣名

# 定義24節氣名稱及對應黃經角度（每隔15度一個）
SOLAR_TERMS = [
    (0, "春分"), (15, "清明"), (30, "穀雨"), (45, "立夏"), (60, "小滿"), (75, "芒種"),
    (90, "夏至"), (105, "小暑"), (120, "大暑"), (135, "立秋"), (150, "處暑"), (165, "白露"),
    (180, "秋分"), (195, "寒露"), (210, "霜降"), (225, "立冬"), (240, "小雪"), (255, "大雪"),
    (270, "冬至"), (285, "小寒"), (300, "大寒"), (315, "立春"), (330, "雨水"), (345, "驚蟄")
]

def get_solar_longitude(dt: datetime) -> float:
    """估算指定日期的太陽視黃經角度（簡化版）"""
    # 計算儒略日（Julian Day Number）
    def julian_day(date: datetime) -> float:
        y = date.year
        m = date.month
        d = date.day + date.hour / 24 + date.minute / 1440 + date.second / 86400

        if m <= 2:
            y -= 1
            m += 12
        A = math.floor(y / 100)
        B = 2 - A + math.floor(A / 4)
        jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5
        return jd

    jd = julian_day(dt)
    n = jd - 2451545.0  # 日數從 J2000.0 起算
    L = (280.46 + 0.9856474 * n) % 360  # 太陽平均黃經（簡化公式）
    return L

def get_nearest_solar_term(date: datetime) -> str:
    """回傳最接近的節氣名稱"""
    longitude = get_solar_longitude(date)
    min_diff = 360
    nearest_term = None
    for deg, name in SOLAR_TERMS:
        diff = abs(longitude - deg)
        if diff < min_diff:
            min_diff = diff
            nearest_term = name
    return nearest_term, round(longitude, 2)

# 測試某日的節氣
test_date = datetime(2025, 1, 1)
term_name, solar_lon = get_nearest_solar_term(test_date)
term_name, solar_lon
