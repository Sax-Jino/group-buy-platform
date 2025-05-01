# 使用官方 Python 3.12 映像作為基礎
FROM python:3.12-slim
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \ 
    libc6-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
# 設定工作目錄
WORKDIR /app

# 複製依賴文件並安裝
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip list
# 複製整個後端程式碼
COPY . .

# 設置環境變數
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 開放端口
EXPOSE 5000

# 運行應用，設定 Gunicorn 的 timeout 和 worker class
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--worker-class", "eventlet", "--timeout", "120", "--workers", "4", "--keep-alive", "65", "app:app"]
