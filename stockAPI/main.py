# app/routers/crawler.py
from fastapi import APIRouter
import httpx

router = APIRouter()


@router.get("/get_stock_day_all")
async def get_stock_day_all():
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": "Failed to fetch data", "status_code": response.status_code}


@router.get("/test")
async def test():
    try:
        from fubon_neo.sdk import FubonSDK, Order
        from fubon_neo.constant import TimeInForce, OrderType, PriceType, MarketType, BSAction

        sdk = FubonSDK()
   
        # accounts = sdk.login("您的身分證字號", "您的登入密碼", "您的憑證位置", "您的憑證密碼") #若有歸戶，則會回傳多筆帳號資訊


        accounts = sdk.login("Q123996512", "z061j4z068","app/stockAPI/Q123996512.pfx","Q123996512")

        print(accounts) #若有多帳號，則回傳多個
        return {"error": "Failed to fetch data"}
    except Exception as e:
        return {"error": str(e)}