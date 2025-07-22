# Use the official lightweight Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy app files
COPY . .

# Streamlit config (optional, avoids sharing button and warnings)
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expose Streamlit port
EXPOSE 7860

# Run the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port=7860", "--server.address=0.0.0.0"]
