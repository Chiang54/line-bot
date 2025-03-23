FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
COPY . .

CMD ["python", "main.py"]
