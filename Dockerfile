FROM python:3.11

WORKDIR /app

# 複製 requirements.txt 並安裝
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 設定環境變數（可以選擇性留著）
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# 複製所有專案檔案
COPY . .

# 開放 Cloud Run 預期的 port
EXPOSE 8080

# ⚡ 用 uvicorn 正確啟動 FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
