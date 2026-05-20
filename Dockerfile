FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed by Playwright Chromium on Debian Bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core
    curl \
    wget \
    ca-certificates \
    # Chromium runtime
    libnss3 \
    libxss1 \
    libatk1.0-0 \
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
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcursor1 \
    libxi6 \
    libxinerama1 \
    libxrender1 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc-s1 \
    libglib2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libuuid1 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    # Virtual display support (Playwright headless does not need this but good to have)
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium browser only (no --with-deps since we installed manually)
RUN playwright install chromium

# Copy project source code
COPY betnacional/ ./betnacional/
COPY main.py .

# Expose FastAPI port
EXPOSE 8001

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
