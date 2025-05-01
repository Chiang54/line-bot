FROM python:3.11

# 安裝 Tesseract OCR 與中文語言包（可選）
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-chi-tra libgl1 libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY routers/captcha_model.pt /app/

# 複製 requirements.txt 並安裝 Python 套件
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 設定環境變數（可以選擇性留著）
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# 複製所有專案檔案
COPY . .

# 開放 Cloud Run 預期的 port
EXPOSE 8080

# 啟動 FastAPI（對應 main.py 裡的 app）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
