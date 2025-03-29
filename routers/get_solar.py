from skyfield.api import load
from skyfield.framelib import ecliptic_frame
from datetime import datetime, timedelta

# 24節氣：太陽到達黃經的角度 (每15°)
solar_terms = [
    '春分', '清明', '穀雨', '立夏', '小滿', '芒種',
    '夏至', '小暑', '大暑', '立秋', '處暑', '白露',
    '秋分', '寒露', '霜降', '立冬', '小雪', '大雪',
    '冬至', '小寒', '大寒', '立春', '雨水', '驚蟄'
]

# 節氣對應角度 (0~360 每隔15°)
solar_term_degrees = {i * 15: solar_terms[i] for i in range(24)}

def get_solar_longitude(ephemeris, ts, date):
    t = ts.utc(date.year, date.month, date.day, 12)  # 中午時間
    sun = ephemeris['sun']
    earth = ephemeris['earth']
    astrometric = earth.at(t).observe(sun).apparent()
    ecliptic = astrometric.frame_latlon(ecliptic_frame)
    longitude = ecliptic[1].degrees
    return longitude

def get_solar_term(date_str):
    # 載入天文資料
    ephemeris = load('de421.bsp')
    ts = load.timescale()

    date = datetime.strptime(date_str, "%Y-%m-%d")
    lon = get_solar_longitude(ephemeris, ts, date)
    
    # 檢查是否有接近節氣角度（容許±1°誤差）
    for deg, term in solar_term_degrees.items():
        if abs((lon - deg + 360) % 360) < 1:  # 處理角度環繞
            return term
    return ''

# 🔍 測試範例
# print(get_solar_term('2025-03-05'))  # 應該是 驚蟄
# print(get_solar_term('2025-03-19'))  # 應該是 ''
# print(get_solar_term('2025-03-20'))  # 應該是 春分
# print(get_solar_term('2025-03-21'))  # 應該是 ''