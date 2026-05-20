FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed by Playwright (Chromium)
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    libnss3 \
    libxss1 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    libasound2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium browser
RUN playwright install chromium --with-deps

# Copy project source code
COPY betnacional/ ./betnacional/
COPY main.py .

# Expose FastAPI port
EXPOSE 8001

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
