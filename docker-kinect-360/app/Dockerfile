FROM kinect-base

# Switch to root user to perform install and permission setup
USER root

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Fix ownership and permissions so devuser can access files
RUN chmod 644 app.py && chown -R devuser:plugdev /app

# Switch back to non-root user before running
USER devuser

CMD ["python3", "app.py"]