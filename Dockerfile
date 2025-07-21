# Stage 1: Use the official Python slim image as a base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
# This leverages Docker's layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
COPY src/ ./src/

# Expose the port the app runs on
EXPOSE 5001

# Define the command to run the application using Gunicorn
# This is the entrypoint for the container
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "src.main:app"]
