# MISO Forge - Production Dockerfile v2.0

# Use an official NVIDIA CUDA base image.
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# Avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies using the OS default python3
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Create a virtual environment using the system's python3
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install dependencies into the virtual environment
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code into the container
COPY . .

# Expose the port the Flask app runs on
EXPOSE 5000

# The command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]
