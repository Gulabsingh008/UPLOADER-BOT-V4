FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y ffmpeg jq python3-dev gcc libffi-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN python3 -m pip check yt-dlp || true

CMD ["python3", "bot.py"]
