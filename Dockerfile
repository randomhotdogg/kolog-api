FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製需求文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY app/ ./app/

# 建立非 root 用戶
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# 設定環境變數
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]