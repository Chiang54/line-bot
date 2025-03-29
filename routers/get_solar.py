import math
from datetime import datetime, timedelta
from skyfield.api import load

# 建立簡化的節氣推算演算法（黃經法）
# 資料來源：近似太陽視黃經計算（精度約±1日），用於辨別節氣名

# 定義24節氣名稱及對應黃經角度（每隔15度一個）
SOLAR_TERMS = [
    (0, "春分"), (15, "清明"), (30, "穀雨"), (45, "立夏"), (60, "小滿"), (75, "芒種"),
    (90, "夏至"), (105, "小暑"), (120, "大暑"), (135, "立秋"), (150, "處暑"), (165, "白露"),
    (180, "秋分"), (195, "寒露"), (210, "霜降"), (225, "立冬"), (240, "小雪"), (255, "大雪"),
    (270, "冬至"), (285, "小寒"), (300, "大寒"), (315, "立春"), (330, "雨水"), (345, "驚蟄")
]

def get_solar_term_skyfield(target_date: datetime) -> str:
    # 使用 skyfield 判斷當天是否是節氣
    eph = load('de421.bsp')
    ts = load.timescale()
    sun, earth = eph['sun'], eph['earth']

    for delta in range(-1, 2):  # 當天及前後各一天
        dt = target_date + timedelta(days=delta)
        t = ts.utc(dt.year, dt.month, dt.day)
        astrometric = earth.at(t).observe(sun).apparent()
        lon, lat, distance = astrometric.ecliptic_latlon()
        solar_longitude = lon.degrees % 360

        for deg, name in SOLAR_TERMS:
            if abs(solar_longitude - deg) < 1:
                if delta == 0:  # 只回傳當天是節氣的情況
                    return name
    return ""