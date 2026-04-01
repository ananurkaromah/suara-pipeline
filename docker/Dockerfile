FROM python:3.11-slim

# Install system dependencies for audio processing & Bruin
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Bruin CLI (2026 Version)
RUN curl -L https://github.com/bruin-data/bruin/releases/latest/download/bruin_Linux_x86_64.tar.gz | tar -xz -C /usr/local/bin

# Set working directory
WORKDIR /app

# Install Python dependencies via uv
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

# Copy the rest of the pipeline
COPY . .

CMD ["tail", "-f", "/dev/null"]