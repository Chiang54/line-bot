import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import router  # 引入 router 模組
from crawler import crawler  # 引入 crawler 模組
from stockAPI import main as st  # 引入 stockAPI 模組
from my_linebot import my_linebot

app = FastAPI()

# 引入路由
app.include_router(router.router, prefix='/router', tags=['基本'])
app.include_router(crawler.router, prefix='/crawler', tags=['爬蟲'])
app.include_router(st.router, prefix='/stockAPI', tags=['證交所'])
app.include_router(my_linebot.router, prefix='/linebot', tags=['LINEAPI'])

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
    port = int(os.getenv('PORT', 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)