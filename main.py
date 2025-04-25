import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import router  # 引入 router 模組
from crawler import crawler  # 引入 crawler 模組
from stockAPI import main as st  # 引入 stockAPI 模組
from Telegram_Bot import main as Telegram_Bot  # 引入 Telegram Bot 模組
from my_linebot import my_linebot
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# 設定允許來源（可根據實際情況限制）
origins = [
    "*",  # 🚨 開放全部來源，如果你要安全建議改成前端網址
    # "https://5174-idx-test-1743212816787.cluster-3g4scxt2njdd6uovkqyfcabgo6.cloudworkstations.dev/", 
]

# 加入 CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # ✅ 開放全部來源
    allow_credentials=False,     # ⚠️ 必須是 False，否則瀏覽器會報錯
    allow_methods=["*"],
    allow_headers=["*"],
)
# 引入路由
app.include_router(router.router, prefix='/router', tags=['基本'])
app.include_router(crawler.router, prefix='/crawler', tags=['爬蟲'])
app.include_router(st.router, prefix='/stockAPI', tags=['證交所'])
app.include_router(my_linebot.router, prefix='/linebot', tags=['LINEAPI'])
app.include_router(Telegram_Bot.router, prefix='/Telegram_Bot', tags=['Telegram機器人'])

# 自訂 404 錯誤處理 
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "此路徑未被允許"}
    )

# 🚀 啟動 FastAPI 應用
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)