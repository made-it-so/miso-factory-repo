# Use a more complete base image that includes common build tools
FROM python:3.11

# Set up the working directory
WORKDIR /app

# Explicitly install curl, which is needed for the code-server install script
RUN apt-get update && apt-get install -y curl

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install code-server (VS Code in the browser)
RUN curl -fsSL https://code-server.dev/install.sh | sh

# Copy the rest of the project files into the container
COPY . .

# Expose the port for code-server
EXPOSE 8080

# Start code-server with no password for easy local access
CMD ["code-server", "--bind-addr", "0.0.0.0:8080", "--auth", "none", "."]
