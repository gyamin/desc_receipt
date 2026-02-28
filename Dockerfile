FROM python:3.12-slim

# 環境変数（ログ周りの定番）
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Tesseract + OCR前処理用ライブラリ
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       tesseract-ocr \
       tesseract-ocr-jpn \
       libtesseract-dev \
       poppler-utils \
       libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体
COPY app/ /app/
# レシートpdfファイル


CMD ["python", "main.py"]