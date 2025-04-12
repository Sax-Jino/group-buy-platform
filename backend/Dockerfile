# 使用官方 Python 3.8 映像作為基礎
FROM python:3.8-slim

# 設定工作目錄
WORKDIR /app

# 複製依賴文件並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個後端程式碼
COPY . .

# 設置環境變數
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 開放端口
EXPOSE 5000

# 運行應用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]