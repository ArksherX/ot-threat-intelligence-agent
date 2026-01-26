# OT Threat Intelligence Agent - Docker Configuration

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data

# Pull Qwen model (this will increase image size significantly)
# Uncomment if you want the model baked into the image
# RUN ollama serve & sleep 5 && ollama pull qwen2.5:latest

# Expose Streamlit port
EXPOSE 8501

# Expose Ollama port
EXPOSE 11434

# Default command (runs the dashboard)
CMD ["streamlit", "run", "src/dashboard.py", "--server.address", "0.0.0.0"]
