FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY detection_engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY detection_engine/ ./detection_engine/

EXPOSE 8002

CMD ["uvicorn", "detection_engine.main:app", "--host", "0.0.0.0", "--port", "8002"]
