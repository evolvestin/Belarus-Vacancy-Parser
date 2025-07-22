FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY root_path.py .
COPY .env .

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.bot"]
