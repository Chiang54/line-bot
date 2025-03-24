# app/routers/crawler.py
from fastapi import APIRouter
import requests
from bs4 import BeautifulSoup
from enum import Enum

router = APIRouter()


class Currency(str, Enum):
    USD = "USD"
    HKD = "HKD"
    GBP = "GBP"
    AUD = "AUD"
    CAD = "CAD"
    SGD = "SGD"
    CHF = "CHF"
    JPY = "JPY"
    ZAR = "ZAR"
    SEK = "SEK"
    NZD = "NZD"
    THB = "THB"
    PHP = "PHP"
    IDR = "IDR"
    EUR = "EUR"
    KRW = "KRW"
    VND = "VND"
    MYR = "MYR"
    CNY = "CNY"


@router.get("/get_history")
async def get_jpy_exchange_rate(currency: Currency):
    coin = currency.value
    url = f"https://rate.bot.com.tw/xrt/quote/ltm/{coin}"
    print(url)
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "無法取得匯率資料"}

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 定位匯率數據表格
    table = soup.find("table", {"class": "table table-striped table-bordered table-condensed table-hover"})
    if not table:
        return {"error": "找不到匯率表格"}

    # 提取所需的匯率資料
    data = []
    rows = table.find("tbody").find_all("tr")
    for row in rows:
        columns = row.find_all("td")
        date = columns[0].get_text(strip=True)
        currency = columns[1].get_text(strip=True)
        cash_buy = columns[2].get_text(strip=True)
        cash_sell = columns[3].get_text(strip=True)
        spot_buy = columns[4].get_text(strip=True)
        spot_sell = columns[5].get_text(strip=True)

        data.append({
            "date": date,
            "currency": currency,
            "cash_buy": cash_buy,
            "cash_sell": cash_sell,
            "spot_buy": spot_buy,
            "spot_sell": spot_sell
        })

    return {"currency": coin, "exchange_rates": data}
