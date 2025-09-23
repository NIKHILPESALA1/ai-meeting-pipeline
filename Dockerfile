# Base image with Python and system tools
FROM python:3.11-slim


# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    unzip \
    gnupg\
    && rm -rf /var/lib/apt/lists/*
# Install Git LFS
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash
RUN apt-get install -y git-lfs
RUN git lfs install

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts
COPY scripts/ ./scripts/

# Create folders for pipeline outputs
RUN mkdir -p /app/meetings /app/audio /app/transcripts /app/summaries

# Default command (runs inside Jenkins pipeline)
CMD ["bash"]
