FROM python:3.10-slim

# Prevents Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (slim base already has pip); add build essentials if needed by libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and assets
COPY . .

# Streamlit default port and network binding
EXPOSE 8501

# Streamlit needs to run on 0.0.0.0 inside the container
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]

