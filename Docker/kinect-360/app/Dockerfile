FROM kinect-base

USER root

WORKDIR /app

# Install system packages needed by OpenCV and other libs
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN chmod 644 app.py && chown -R devuser:plugdev /app

USER devuser

CMD ["python3", "app.py"]