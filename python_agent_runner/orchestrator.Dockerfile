# Use the same base Python version for consistency
FROM python:3.11

# Set up the working directory and add all project files
WORKDIR /app
COPY . .

# Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

# The command to run the autonomous loop
CMD ["python", "miso_main.py"]
