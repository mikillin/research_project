FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1\
    libglib2.0-0 \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY camera_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY camera_service/ ./camera_service/

EXPOSE 8001

CMD ["uvicorn", "camera_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
