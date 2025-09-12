# Use an official Python runtime as a parent image
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run app.py with an extended 10-minute timeout for the LLM
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "600", "app:app"]
